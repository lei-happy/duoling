"""
租户管理服务
"""

from typing import Optional, Tuple, List, Callable, Awaitable
from datetime import datetime, timedelta

from sqlalchemy import select, func, exists, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.tenant.tenant_product import TenantProduct
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.console.schemas.tenant.tenant import (
    TenantCreate, TenantUpdate, TenantOut, TenantListOut,
    TenantProductCreate, TenantProductOut,
    TenantFollowPoolUpdate,
)
from app.modules.console.services.system.open_register_policy_service import (
    OpenRegisterPolicyService,
)

# on_progress(step_key, message, percent)
TenantCreateProgressCallback = Optional[Callable[[str, str, int], Awaitable[None]]]


class TenantService:
    """租户管理服务"""

    @staticmethod
    def _active_product_exists(version_code_filter=None, exclude_basic=False):
        """生成有效授权的 EXISTS 子查询条件"""
        conds = [
            TenantProduct.tenant_id == Tenant.id,
            TenantProduct.is_deleted == 0,
            TenantProduct.status == 1,
            or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > datetime.now()),
        ]
        if version_code_filter:
            conds.append(TenantProduct.version_code == version_code_filter)
        if exclude_basic:
            conds.append(TenantProduct.version_code != "basic")
        return exists(select(TenantProduct.id).where(*conds))

    @staticmethod
    def _active_commercial_non_basic_exists(version_code_filter=None):
        """有效「商业」非 basic：grant_type 为 trial 的自助试用不算付费客户"""
        conds = [
            TenantProduct.tenant_id == Tenant.id,
            TenantProduct.is_deleted == 0,
            TenantProduct.status == 1,
            TenantProduct.version_code != "basic",
            or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > datetime.now()),
            or_(TenantProduct.grant_type.is_(None), TenantProduct.grant_type != "trial"),
        ]
        if version_code_filter:
            conds.append(TenantProduct.version_code == version_code_filter)
        return exists(select(TenantProduct.id).where(*conds))

    @staticmethod
    def _any_active_product_exists():
        """任意当前有效的产品授权"""
        conds = [
            TenantProduct.tenant_id == Tenant.id,
            TenantProduct.is_deleted == 0,
            TenantProduct.status == 1,
            or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > datetime.now()),
        ]
        return exists(select(TenantProduct.id).where(*conds))

    # ============================================================
    # 租户 CRUD
    # ============================================================

    @staticmethod
    async def create_tenant(
        db: AsyncSession,
        data: TenantCreate,
        on_progress: TenantCreateProgressCallback = None,
    ) -> Tuple[Tenant, bool]:
        """
        创建新租户
        1. 生成租户编码
        2. 创建租户记录
        3. 创建租户独立数据库
        4. 关联或创建管理员账号

        返回: (tenant, is_existing_user)
            is_existing_user=True 表示管理员账号已存在（手机号已注册过）

        on_progress: 可选，官网异步注册时上报阶段进度 (step_key, message, percent)
        """
        async def _emit(step_key: str, message: str, percent: int) -> None:
            if on_progress:
                await on_progress(step_key, message, percent)

        # 检查企业名称是否重复
        existing = await db.execute(
            select(Tenant).where(
                Tenant.tenant_name == data.tenantName,
                Tenant.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException("企业名称已存在")

        # 生成租户编码（基于自增序号）
        max_id_result = await db.execute(
            select(func.max(Tenant.id))
        )
        max_id = max_id_result.scalar() or 0
        tenant_code = str(1001 + max_id)

        settings = get_settings()
        db_name = settings.tenant_database_name(tenant_code)

        source_ch = data.sourceChannel or "console"
        # carrier_invite 渠道：承运商邀请激活，复用自助注册策略路径但默认强制开通 lite
        use_open_register_policy = source_ch in (
            "website", "referral", "carrier_invite"
        )
        policy_version_code = "basic"
        policy_trial_days = 0
        if use_open_register_policy:
            if source_ch == "carrier_invite":
                # 承运商邀请固定开通 lite 不限期，不读取自助注册策略
                policy_version_code = "lite"
                policy_trial_days = 0
            else:
                policy_version_code, policy_trial_days = (
                    await OpenRegisterPolicyService.get_policy_raw(db)
                )

        remark = data.remark
        if use_open_register_policy and source_ch != "carrier_invite":
            if policy_trial_days > 0:
                remark = f"官网自助注册（{policy_trial_days}天试用）"
            else:
                remark = "官网自助注册（不限期体验）"
        elif source_ch == "carrier_invite" and not remark:
            invite_src = data.inviteSourceTenant or "未知"
            remark = f"承运商邀请激活（来源租户 {invite_src}）"

        # 创建租户记录
        tenant = Tenant(
            tenant_code=tenant_code,
            tenant_name=data.tenantName,
            short_name=data.shortName,
            contact_person=data.contactPerson,
            contact_phone=data.contactPhone,
            contact_email=data.contactEmail,
            province=data.province,
            city=data.city,
            address=data.address,
            license_no=data.licenseNo,
            status=1,  # 注册即激活
            db_name=db_name,
            remark=remark,
            source_channel=source_ch,
            referrer_code=data.referrerCode,
        )
        db.add(tenant)
        await db.flush()
        await _emit("tenant_record", "创建企业信息", 10)

        # 创建租户独立数据库（仅 core 层表）
        try:
            import app.modules.client.models  # noqa: F401
            await _emit("tenant_database", "初始化独立数据库", 25)
            await db_manager.create_tenant_database(tenant_code)
            await _emit("seed_data", "初始化组织架构与角色", 40)
            await TenantService._init_tenant_seed_data(
                tenant_code,
                admin_name=data.contactPerson or "管理员",
                admin_phone=data.contactPhone,
                admin_email=data.contactEmail,
                on_progress=on_progress,
            )
            tenant.db_initialized = 1
        except Exception as e:
            logger.error(f"创建租户数据库失败: {e}")
            tenant.db_initialized = 0

        # ---- 管理员账号：按手机号查找已有用户 ----
        await _emit("admin_binding", "配置管理员账号", 85)
        is_existing_user = False
        admin_user = None

        if data.contactPhone:
            result = await db.execute(
                select(User).where(
                    User.phone == data.contactPhone,
                    User.is_deleted == 0,
                )
            )
            admin_user = result.scalar_one_or_none()

        if admin_user:
            # 已有用户 —— 复用，不创建新 User
            is_existing_user = True
            logger.info(
                f"手机号 {data.contactPhone} 已存在用户(id={admin_user.id})，"
                f"复用该用户关联新企业 {tenant_code}"
            )
        else:
            # 新用户 —— 创建 User
            admin_user = User(
                password=hash_password("123456"),
                real_name=data.contactPerson or "管理员",
                phone=data.contactPhone,
                email=data.contactEmail,
                user_type=2,
                status=1,
                force_change_pwd=1,
            )
            db.add(admin_user)
            await db.flush()

        # 创建用户-企业关联（检查是否已存在）
        existing_ut = await db.execute(
            select(UserTenant).where(
                UserTenant.user_id == admin_user.id,
                UserTenant.tenant_code == tenant_code,
            )
        )
        ut_record = existing_ut.scalar_one_or_none()
        if ut_record:
            ut_record.user_type = 1
            ut_record.status = 1
            ut_record.is_deleted = 0
            if source_ch == "carrier_invite" and data.inviteSourceTenant:
                ut_record.invite_source_tenant = data.inviteSourceTenant
        else:
            db.add(UserTenant(
                user_id=admin_user.id,
                tenant_code=tenant_code,
                user_type=1,
                status=1,
                invite_source_tenant=(
                    data.inviteSourceTenant
                    if source_ch == "carrier_invite" else None
                ),
            ))

        # 自动开通产品版本：
        #   - website / referral：按运营配置（policy_version_code/policy_trial_days）
        #   - carrier_invite：固定 lite 不限期
        #   - console：basic 不限期
        # 所有路径开通授权后都统一调用 _ensure_version_tables，使得 basic / lite / standard
        # 等任意版本所需的 business 层表都按 sys_product_feature.required_tables 自动创建。
        granted_version_id: Optional[int] = None
        if use_open_register_policy:
            pv = await OpenRegisterPolicyService.get_resolved_version(
                db, policy_version_code
            )
            start_t = datetime.now()
            end_t = (
                start_t + timedelta(days=policy_trial_days)
                if policy_trial_days > 0
                else None
            )
            grant_remark = (
                "承运商邀请激活" if source_ch == "carrier_invite"
                else "官网自助注册"
            )
            db.add(
                TenantProduct(
                    tenant_id=tenant.id,
                    tenant_code=tenant_code,
                    version_id=pv.id,
                    version_code=pv.version_code,
                    start_time=start_t,
                    end_time=end_t,
                    status=1,
                    grant_type=OpenRegisterPolicyService.grant_type_for_self_register(),
                    grant_remark=grant_remark,
                )
            )
            if end_t is not None:
                tenant.expire_time = end_t
            granted_version_id = pv.id
        else:
            basic_ver = await db.execute(
                select(ProductVersion).where(
                    ProductVersion.version_code == "basic",
                    ProductVersion.status == 1,
                    ProductVersion.is_deleted == 0,
                )
            )
            basic_version = basic_ver.scalar_one_or_none()
            if basic_version:
                db.add(
                    TenantProduct(
                        tenant_id=tenant.id,
                        tenant_code=tenant_code,
                        version_id=basic_version.id,
                        version_code="basic",
                        start_time=datetime.now(),
                        end_time=None,
                        status=1,
                    )
                )
                granted_version_id = basic_version.id

        await db.flush()

        # 统一按当前授权版本的 required_tables 建业务表
        # （basic 也走这里，承运商三表挂在 partner_carrier.required_tables，
        #  basic 包含 partner_carrier 时即会自动建表）
        if granted_version_id is not None:
            try:
                await TenantService._ensure_version_tables(
                    db, tenant_code, granted_version_id
                )
            except Exception as e:
                logger.warning(
                    f"租户 {tenant_code} 开户按需建业务表失败（非致命）: {e}"
                )
        await _emit("done", "开户完成", 100)
        logger.info(f"新租户已创建: {tenant_code} - {data.tenantName}")

        return tenant, is_existing_user

    @staticmethod
    async def _init_tenant_seed_data(
        tenant_code: str,
        admin_name: str = "管理员",
        admin_phone: Optional[str] = None,
        admin_email: Optional[str] = None,
        on_progress: TenantCreateProgressCallback = None,
    ) -> None:
        """
        在租户库中插入种子数据：默认角色、部门、管理员及关联。
        通过平台库同步地区数据到 biz_region。
        """
        from app.modules.client.models.role.biz_role import BizRole
        from app.modules.client.models.organization.biz_department import BizDepartment
        from app.modules.client.models.organization.business_entity import BusinessEntity
        from app.modules.client.models.user.biz_user import BizUser
        from app.modules.client.models.user.biz_user_role import BizUserRole
        from app.modules.client.models.biz_dict import BizDict, BizDictItem
        from app.modules.client.models.system_config import SystemConfig

        engine = db_manager._get_or_create_tenant_engine(tenant_code)
        session_factory = db_manager._tenant_session_factories[tenant_code]

        async with session_factory() as session:
            try:
                # 默认角色（仅管理员）
                roles = [
                    BizRole(
                        role_code="admin",
                        role_name="管理员",
                        sort_order=0,
                        status=1,
                        remark="拥有系统全部的操作权限",
                    ),
                ]
                session.add_all(roles)
                await session.flush()

                # 默认部门
                hq = BizDepartment(parent_id=0, dept_name="总公司", dept_code="HQ", dept_type="headquarters", sort_order=0, status=1)
                session.add(hq)
                await session.flush()
                sub_depts = [
                    BizDepartment(parent_id=hq.id, dept_name="运营部", dept_code="OP", dept_type="department", sort_order=0, status=1),
                    BizDepartment(parent_id=hq.id, dept_name="车队部", dept_code="FL", dept_type="fleet", sort_order=10, status=1),
                    BizDepartment(parent_id=hq.id, dept_name="财务部", dept_code="FI", dept_type="department", sort_order=20, status=1),
                ]
                session.add_all(sub_depts)
                await session.flush()

                # 默认经营主体（法人/独立核算单元；分主体对账的归属维度）
                default_entity = BusinessEntity(
                    entity_code="ENT0001",
                    entity_name="默认经营主体",
                    invoice_title="默认经营主体",
                    is_default=1,
                    status=1,
                    sort_order=0,
                )
                session.add(default_entity)
                await session.flush()

                # 管理员用户
                admin_user = BizUser(
                    password=hash_password("123456"),
                    real_name=admin_name,
                    phone=admin_phone,
                    email=admin_email,
                    user_type=1,
                    department_id=hq.id,
                    status=0,
                )
                session.add(admin_user)
                await session.flush()

                # 管理员-角色关联
                admin_role = roles[0]
                user_role = BizUserRole(user_id=admin_user.id, role_id=admin_role.id)
                session.add(user_role)

                # 基础字典数据（统一来源）
                from scripts.seed.seed_client_dicts import DICT_DEFS

                for dict_code, dict_name, sort_order, items in DICT_DEFS:
                    d = BizDict(
                        dict_code=dict_code,
                        dict_name=dict_name,
                        sort_order=sort_order,
                        status=1,
                    )
                    session.add(d)
                    await session.flush()
                    for item_name, item_value, item_sort in items:
                        session.add(BizDictItem(
                            dict_id=d.id,
                            dict_code=dict_code,
                            item_name=item_name,
                            item_value=item_value,
                            sort_order=item_sort,
                        ))

                # 系统配置初始数据
                default_configs = [
                    SystemConfig(
                        config_key="waybill.freight_calc_mode",
                        config_value="auto_preferred",
                        config_group="waybill",
                        description="运费计算模式：auto_required-强制自动计费 auto_preferred-优先自动允许手动 manual_only-仅手动",
                        value_type="enum",
                        default_value="auto_preferred",
                    ),
                    SystemConfig(
                        config_key="waybill.list_show_freight_amount",
                        config_value="false",
                        config_group="waybill",
                        description="运单列表是否展示运费金额（敏感信息，默认关闭）",
                        value_type="boolean",
                        default_value="false",
                    ),
                    SystemConfig(
                        config_key="waybill.auto_confirm_on_create",
                        config_value="false",
                        config_group="waybill",
                        description="新建/导入运单时是否自动完成确认（关闭：待确认；开启：直接进入待调度）",
                        value_type="boolean",
                        default_value="false",
                    ),
                    SystemConfig(
                        config_key="task.no_gen_rule",
                        config_value='{"parts":[{"type":"prefix","value":"TASK"},'
                        '{"type":"date","format":"YYYYMMDD"},'
                        '{"type":"seq","digits":4,"reset":"daily"}]}',
                        config_group="task",
                        description="任务单号生成规则 JSON（parts 三段 prefix/date/seq）",
                        value_type="json",
                        default_value='{"parts":[{"type":"prefix","value":"TASK"},'
                        '{"type":"date","format":"YYYYMMDD"},'
                        '{"type":"seq","digits":4,"reset":"daily"}]}',
                    ),
                    SystemConfig(
                        config_key="task.name_gen_rule",
                        config_value='{"joiner":" ","parts":[{"kind":"route_od"},'
                        '{"kind":"vehicle_first"},{"kind":"carrier_driver_plate"}]}',
                        config_group="task",
                        description="任务名称生成规则 JSON（joiner + parts 三段 kind）",
                        value_type="json",
                        default_value='{"joiner":" ","parts":[{"kind":"route_od"},'
                        '{"kind":"vehicle_first"},{"kind":"carrier_driver_plate"}]}',
                    ),
                    SystemConfig(
                        config_key="system.watermark_enabled",
                        config_value="false",
                        config_group="security",
                        description="是否启用页面水印（默认关闭）",
                        value_type="boolean",
                        default_value="false",
                    ),
                    SystemConfig(
                        config_key="system.watermark_content",
                        config_value="{nickname} {phoneLast4} {date}",
                        config_group="security",
                        description="页面水印文本模板，支持 {nickname} {phoneLast4} {date} 等变量",
                        value_type="string",
                        default_value="{nickname} {phoneLast4} {date}",
                    ),
                    SystemConfig(
                        config_key="system.watermark_style",
                        config_value='{"fontSize":14,"color":"rgba(0, 0, 0, 0.12)",'
                        '"rotate":-22,"gap":[200,160],"zIndex":9999}',
                        config_group="security",
                        description="页面水印样式 JSON：fontSize/color/rotate/gap/zIndex",
                        value_type="json",
                        default_value='{"fontSize":14,"color":"rgba(0, 0, 0, 0.12)",'
                        '"rotate":-22,"gap":[200,160],"zIndex":9999}',
                    ),
                ]
                session.add_all(default_configs)

                await session.commit()
                logger.info(f"租户 {tenant_code} 种子数据已初始化")
            except Exception as e:
                await session.rollback()
                logger.error(f"租户 {tenant_code} 种子数据初始化失败: {e}")
                raise

        # 同步地区数据（从平台 sys_regions 到租户 biz_region）
        try:
            if on_progress:
                await on_progress("region_sync", "初始化地区数据", 52)
            await TenantService._sync_region_data(tenant_code)
        except Exception as e:
            logger.warning(f"租户 {tenant_code} 地区数据同步失败（非致命）: {e}")

        # 同步品牌/车系（平台 basicdata_brand / basicdata_car_series → 租户）
        try:
            if on_progress:
                await on_progress("vehicle_sync", "初始化车型数据", 65)
            await TenantService._sync_vehicle_brand_series(tenant_code)
        except Exception as e:
            logger.warning(
                f"租户 {tenant_code} 车型基础数据同步失败（非致命）: {e}"
            )

        # 同步经销商（平台 basicdata_dealer_info → 租户 biz_dealer）
        try:
            if on_progress:
                await on_progress("dealer_sync", "初始化经销商数据", 72)
            await TenantService._sync_dealer_data(tenant_code)
        except Exception as e:
            logger.warning(
                f"租户 {tenant_code} 经销商数据同步失败（非致命）: {e}"
            )

    @staticmethod
    async def _sync_region_data(tenant_code: str) -> None:
        """从平台 sys_regions 同步地区数据到租户库 biz_region"""
        settings = get_settings()
        platform_db = settings.platform_database_name

        engine = db_manager._get_or_create_tenant_engine(tenant_code)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM biz_region"))
            if (result.scalar() or 0) > 0:
                logger.info(f"租户 {tenant_code} biz_region 已有数据，跳过同步")
                return

            # 先检查 sys_regions 表的列结构，动态映射到 biz_region
            cols_result = await conn.execute(text(
                f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'sys_regions' "
                f"ORDER BY ORDINAL_POSITION"
            ), {"db": platform_db})
            source_cols = [row[0] for row in cols_result]
            logger.info(f"sys_regions 列: {source_cols}")

            # biz_region 目标列 -> sys_regions 可能的源列名映射
            col_candidates = {
                "code": ["code", "region_code", "area_code"],
                "name": ["name", "region_name", "area_name"],
                "parent_code": ["parent_code", "parent_id", "pid", "pcode"],
                "level": ["level", "region_level", "deep", "depth", "type"],
                "sort_order": ["sort_order", "sort", "order_num"],
                "status": ["status"],
                "longitude": ["longitude", "lng"],
                "latitude": ["latitude", "lat"],
            }

            mapping = {}
            for target, candidates in col_candidates.items():
                for c in candidates:
                    if c in source_cols:
                        mapping[target] = c
                        break

            if "code" not in mapping or "name" not in mapping:
                logger.error(
                    f"sys_regions 列名无法映射到 biz_region，"
                    f"源列: {source_cols}，已匹配: {mapping}"
                )
                return

            # 构建动态 INSERT ... SELECT
            target_cols = list(mapping.keys())
            source_exprs = []
            for t in target_cols:
                src_col = mapping[t]
                if t in ("code", "parent_code"):
                    source_exprs.append(f"CAST(`{src_col}` AS CHAR)")
                else:
                    source_exprs.append(f"`{src_col}`")

            # 缺失的列提供默认值
            if "parent_code" not in mapping:
                target_cols.append("parent_code")
                source_exprs.append("NULL")
            if "level" not in mapping:
                target_cols.append("level")
                source_exprs.append("1")
            if "sort_order" not in mapping:
                target_cols.append("sort_order")
                source_exprs.append("0")
            if "status" not in mapping:
                target_cols.append("status")
                source_exprs.append("1")

            # is_deleted 必须显式赋值（biz_region 表该列可能无 DB 级默认值）
            target_cols.append("is_deleted")
            source_exprs.append("0")

            # source=0 标记为系统初始化数据（不可编辑/删除）
            target_cols.append("source")
            source_exprs.append("0")

            # 构建 WHERE 条件：仅同步未删除的省/市/区三级数据
            where_parts = []
            if "is_deleted" in source_cols:
                where_parts.append("`is_deleted` = 0")
            if "level" in source_cols:
                where_parts.append("`level` <= 3")
            where_clause = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

            insert_sql = (
                f"INSERT INTO biz_region ({', '.join(target_cols)}) "
                f"SELECT {', '.join(source_exprs)} "
                f"FROM `{platform_db}`.sys_regions{where_clause}"
            )
            logger.info(f"地区同步 SQL: {insert_sql}")
            await conn.execute(text(insert_sql))

        logger.info(f"租户 {tenant_code} 地区数据已从平台同步")

    @staticmethod
    async def _sync_vehicle_brand_series(tenant_code: str) -> None:
        """从平台 basicdata_brand / basicdata_car_series 同步到租户库"""
        settings = get_settings()
        platform_db = settings.platform_database_name
        engine = db_manager._get_or_create_tenant_engine(tenant_code)

        async with engine.begin() as conn:
            async def _count(table: str) -> int:
                try:
                    r = await conn.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                    return int(r.scalar() or 0)
                except Exception:
                    return -1

            brand_cnt = await _count("biz_vehicle_brand")
            if brand_cnt < 0:
                logger.warning(
                    f"租户 {tenant_code} 无 biz_vehicle_brand 表，跳过车型数据同步"
                )
                return

            if brand_cnt == 0:
                await conn.execute(
                    text(
                        f"INSERT INTO biz_vehicle_brand ("
                        f"brand_id, brand_logo, brand_name_cn, brand_country, "
                        f"brand_introduce, create_time, last_update_time) "
                        f"SELECT brand_id, brand_logo, brand_name_cn, brand_country, "
                        f"brand_introduce, create_time, last_update_time "
                        f"FROM `{platform_db}`.basicdata_brand"
                    )
                )
                logger.info(f"租户 {tenant_code} 品牌数据已从平台同步")
            else:
                logger.info(
                    f"租户 {tenant_code} biz_vehicle_brand 已有数据，跳过品牌同步"
                )

            if await _count("biz_vehicle_series") == 0:
                await conn.execute(
                    text(
                        f"INSERT INTO biz_vehicle_series ("
                        f"series_id, brand_id, price, series_image, series_name, "
                        f"energy_type, length_mm, width_mm, height_mm, wheelbase_mm, "
                        f"front_track_mm, rear_track_mm, approach_angle, "
                        f"departure_angle, curb_weight_kg, create_time, last_update_time) "
                        f"SELECT series_id, brand_id, price, series_image, series_name, "
                        f"energy_type, length_mm, width_mm, height_mm, wheelbase_mm, "
                        f"front_track_mm, rear_track_mm, approach_angle, "
                        f"departure_angle, curb_weight_kg, create_time, last_update_time "
                        f"FROM `{platform_db}`.basicdata_car_series"
                    )
                )
                logger.info(f"租户 {tenant_code} 车系数据已从平台同步")
            else:
                logger.info(
                    f"租户 {tenant_code} biz_vehicle_series 已有数据，跳过车系同步"
                )

    @staticmethod
    async def _sync_dealer_data(tenant_code: str) -> None:
        """从平台 basicdata_dealer_info 同步到租户 biz_dealer"""
        settings = get_settings()
        platform_db = settings.platform_database_name
        engine = db_manager._get_or_create_tenant_engine(tenant_code)

        async with engine.begin() as conn:
            try:
                r = await conn.execute(text("SELECT COUNT(*) FROM `biz_dealer`"))
                dealer_cnt = int(r.scalar() or 0)
            except Exception:
                logger.warning(
                    f"租户 {tenant_code} 无 biz_dealer 表，跳过经销商数据同步"
                )
                return

            if dealer_cnt == 0:
                await conn.execute(
                    text(
                        f"INSERT INTO biz_dealer ("
                        f"dealer_id, dealer_name, dealer_type, main_brand, "
                        f"province, city, address_detail, longitude, latitude, "
                        f"created_at, updated_at) "
                        f"SELECT dealer_id, dealer_name, dealer_type, main_brand, "
                        f"province, city, address_detail, longitude, latitude, "
                        f"created_at, updated_at "
                        f"FROM `{platform_db}`.basicdata_dealer_info"
                    )
                )
                logger.info(f"租户 {tenant_code} 经销商数据已从平台同步")
            else:
                logger.info(f"租户 {tenant_code} biz_dealer 已有数据，跳过经销商同步")

    @staticmethod
    async def page_tenants(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        lifecycle: Optional[str] = None,
        version_code: Optional[str] = None,
        expire_warning: bool = False,
    ) -> dict:
        """分页查询租户（返回前端 ele-pro-table 期望的格式）"""
        query = select(Tenant).where(Tenant.is_deleted == 0)

        if keyword:
            query = query.where(
                Tenant.tenant_name.contains(keyword)
                | Tenant.tenant_code.contains(keyword)
                | Tenant.contact_person.contains(keyword)
            )
        if status is not None:
            query = query.where(Tenant.status == status)

        # 生命周期筛选
        if lifecycle == "new":
            cutoff = datetime.now() - timedelta(days=30)
            query = query.where(Tenant.status == 1, Tenant.created_at >= cutoff)
        elif lifecycle == "trial":
            has_any_active = TenantService._any_active_product_exists()
            has_commercial = TenantService._active_commercial_non_basic_exists()
            query = query.where(
                Tenant.status == 1, has_any_active, ~has_commercial
            )
        elif lifecycle == "follow_up":
            query = query.where(Tenant.in_follow_pool == 1)
        elif lifecycle == "paid":
            has_commercial = TenantService._active_commercial_non_basic_exists()
            query = query.where(Tenant.status == 1, has_commercial)
            if version_code:
                version_cond = TenantService._active_commercial_non_basic_exists(
                    version_code_filter=version_code
                )
                query = query.where(version_cond)
            if expire_warning:
                warning_deadline = datetime.now() + timedelta(days=30)
                query = query.where(
                    Tenant.expire_time.isnot(None),
                    Tenant.expire_time <= warning_deadline,
                )
        elif lifecycle == "churned":
            query = query.where(Tenant.status.in_([0, 3]))

        # 总数
        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        # 分页数据
        query = query.order_by(Tenant.id.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        items = list(result.scalars().all())

        # 按版本筛选时，用该版本的最后到期时间替代租户整体到期时间
        version_expire_map: dict = {}
        if version_code and items:
            tenant_ids = [t.id for t in items]
            ve_result = await db.execute(
                select(
                    TenantProduct.tenant_id,
                    func.max(TenantProduct.end_time).label("max_end_time")
                ).where(
                    TenantProduct.tenant_id.in_(tenant_ids),
                    TenantProduct.version_code == version_code,
                    TenantProduct.is_deleted == 0,
                    TenantProduct.status == 1,
                ).group_by(TenantProduct.tenant_id)
            )
            version_expire_map = {
                row.tenant_id: row.max_end_time for row in ve_result
            }

        # 实时计算每个租户的"当前生效版本"，避免依赖 sys_tenant 反范式字段。
        # 选取规则：优先取所有有效授权中 end_time 最晚的（NULL=永久 当作最大），
        # 同期则取 created_at 最新的。这样直接改 DB 的脏数据也能被列表如实呈现。
        current_version_map: dict = {}
        active_count_map: dict = {}
        if items:
            tenant_ids = [t.id for t in items]
            now = datetime.now()
            cv_result = await db.execute(
                select(
                    TenantProduct.tenant_id,
                    TenantProduct.version_id,
                    TenantProduct.version_code,
                    TenantProduct.start_time,
                    TenantProduct.end_time,
                    TenantProduct.created_at,
                    ProductVersion.version_name,
                ).join(
                    ProductVersion,
                    ProductVersion.id == TenantProduct.version_id,
                ).where(
                    TenantProduct.tenant_id.in_(tenant_ids),
                    TenantProduct.is_deleted == 0,
                    TenantProduct.status == 1,
                    or_(
                        TenantProduct.end_time.is_(None),
                        TenantProduct.end_time > now,
                    ),
                    ProductVersion.is_deleted == 0,
                )
            )
            grouped: dict = {}
            for row in cv_result.all():
                grouped.setdefault(row.tenant_id, []).append(row)
            for tid, rows in grouped.items():
                active_count_map[tid] = len(rows)
                # end_time=None 永久 视为最大；同期取 created_at 最新
                rows.sort(
                    key=lambda r: (
                        r.end_time is None,
                        r.end_time or datetime.min,
                        r.created_at or datetime.min,
                    ),
                    reverse=True,
                )
                top = rows[0]
                current_version_map[tid] = {
                    "code": top.version_code,
                    "name": top.version_name,
                }

        out_list = []
        for t in items:
            item = TenantListOut.from_model(t).model_dump()
            if version_code and t.id in version_expire_map:
                ve = version_expire_map[t.id]
                item["expireTime"] = ve.strftime("%Y-%m-%d %H:%M:%S") if ve else None
            cv = current_version_map.get(t.id)
            if cv:
                item["currentVersionCode"] = cv["code"]
                item["currentVersionName"] = cv["name"]
            item["activeProductCount"] = active_count_map.get(t.id, 0)
            out_list.append(item)

        return {
            "list": out_list,
            "count": count,
        }

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: int) -> Optional[Tenant]:
        """根据ID获取租户"""
        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id, Tenant.is_deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenant_by_code(db: AsyncSession, tenant_code: str) -> Optional[Tenant]:
        """根据编码获取租户"""
        result = await db.execute(
            select(Tenant).where(
                Tenant.tenant_code == tenant_code, Tenant.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_tenant(
        db: AsyncSession, data: TenantUpdate
    ) -> Tenant:
        """更新租户信息"""
        tenant = await TenantService.get_tenant_by_id(db, data.id)
        if not tenant:
            raise BizException("租户不存在")

        # 如果修改了企业名称，检查唯一性
        if data.tenantName is not None and data.tenantName != tenant.tenant_name:
            dup = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_name == data.tenantName,
                    Tenant.id != data.id,
                    Tenant.is_deleted == 0,
                )
            )
            if dup.scalar_one_or_none():
                raise BizException("企业名称已存在")
            tenant.tenant_name = data.tenantName

        if data.shortName is not None:
            tenant.short_name = data.shortName
        if data.contactPerson is not None:
            tenant.contact_person = data.contactPerson
        if data.contactPhone is not None:
            tenant.contact_phone = data.contactPhone
        if data.contactEmail is not None:
            tenant.contact_email = data.contactEmail
        if data.province is not None:
            tenant.province = data.province
        if data.city is not None:
            tenant.city = data.city
        if data.address is not None:
            tenant.address = data.address
        if data.logo is not None:
            tenant.logo = data.logo
        if data.licenseNo is not None:
            tenant.license_no = data.licenseNo
        if data.remark is not None:
            tenant.remark = data.remark

        await db.flush()
        return tenant

    @staticmethod
    async def update_status(db: AsyncSession, tenant_id: int, status: int) -> None:
        """更新租户状态（重新激活时自动补齐 basic 授权）"""
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise BizException("租户不存在")
        tenant.status = status

        # 重新激活时确保有 basic 授权
        if status == 1:
            now = datetime.now()
            basic_result = await db.execute(
                select(TenantProduct).where(
                    TenantProduct.tenant_id == tenant_id,
                    TenantProduct.version_code == "basic",
                    TenantProduct.is_deleted == 0,
                    TenantProduct.status == 1,
                    or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > now),
                )
            )
            if not basic_result.scalar_one_or_none():
                basic_ver = await db.execute(
                    select(ProductVersion).where(
                        ProductVersion.version_code == "basic",
                        ProductVersion.status == 1,
                        ProductVersion.is_deleted == 0,
                    )
                )
                basic_version = basic_ver.scalar_one_or_none()
                if basic_version:
                    basic_product = TenantProduct(
                        tenant_id=tenant_id,
                        tenant_code=tenant.tenant_code,
                        version_id=basic_version.id,
                        version_code="basic",
                        start_time=now,
                        end_time=None,
                        status=1,
                    )
                    db.add(basic_product)
                    logger.info(f"租户 {tenant.tenant_code} 重新激活，已自动补齐 basic 授权")

        await db.flush()

    @staticmethod
    async def batch_delete(db: AsyncSession, tenant_ids: List[int]) -> None:
        """批量删除租户（软删除）"""
        result = await db.execute(
            select(Tenant).where(Tenant.id.in_(tenant_ids), Tenant.is_deleted == 0)
        )
        tenants = result.scalars().all()
        for t in tenants:
            t.is_deleted = 1
        await db.flush()

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: int) -> bool:
        """删除租户（软删除）"""
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise BizException("租户不存在")

        tenant.is_deleted = 1
        await db.flush()
        return True

    # ============================================================
    # 跟进池
    # ============================================================

    @staticmethod
    async def update_follow_pool(
        db: AsyncSession, data: TenantFollowPoolUpdate
    ) -> None:
        """标记/移出跟进池"""
        tenant = await TenantService.get_tenant_by_id(db, data.id)
        if not tenant:
            raise BizException("租户不存在")
        tenant.in_follow_pool = data.inFollowPool
        if data.followRemark is not None:
            tenant.follow_remark = data.followRemark
        await db.flush()

    # ============================================================
    # 生命周期统计
    # ============================================================

    @staticmethod
    async def lifecycle_stats(db: AsyncSession) -> dict:
        """各生命周期阶段客户数量"""
        base = select(func.count()).where(Tenant.is_deleted == 0)
        cutoff = datetime.now() - timedelta(days=30)

        has_any_active = TenantService._any_active_product_exists()
        has_commercial = TenantService._active_commercial_non_basic_exists()

        new_q = base.where(Tenant.status == 1, Tenant.created_at >= cutoff)
        trial_q = base.where(
            Tenant.status == 1, has_any_active, ~has_commercial
        )
        follow_q = base.where(Tenant.in_follow_pool == 1)
        paid_q = base.where(Tenant.status == 1, has_commercial)
        churned_q = base.where(Tenant.status.in_([0, 3]))
        total_q = base

        results = {}
        for key, q in [
            ("new", new_q), ("trial", trial_q), ("followUp", follow_q),
            ("paid", paid_q), ("churned", churned_q), ("all", total_q),
        ]:
            r = await db.execute(q)
            results[key] = r.scalar() or 0
        return results

    # ============================================================
    # 租户产品授权
    # ============================================================

    @staticmethod
    async def list_tenant_products(
        db: AsyncSession, tenant_id: int
    ) -> List[TenantProductOut]:
        """查询企业已授权的产品列表"""
        result = await db.execute(
            select(TenantProduct).where(
                TenantProduct.tenant_id == tenant_id,
                TenantProduct.is_deleted == 0,
            ).order_by(TenantProduct.id.desc())
        )
        items = result.scalars().all()
        return [TenantProductOut.from_model(p) for p in items]

    @staticmethod
    async def assign_product(
        db: AsyncSession, tenant_id: int, data: TenantProductCreate
    ) -> TenantProduct:
        """为企业开通产品版本授权"""
        # 查找租户
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise BizException("租户不存在")

        # 解析时间
        start_time = None
        end_time = None
        if data.startTime:
            start_time = datetime.strptime(data.startTime, "%Y-%m-%d %H:%M:%S")
        if data.endTime:
            end_time = datetime.strptime(data.endTime, "%Y-%m-%d %H:%M:%S")

        if start_time and end_time and start_time >= end_time:
            raise BizException("授权开始时间必须早于到期时间")

        # 校验授权时间范围不能与已有授权产生交叉
        existing_result = await db.execute(
            select(TenantProduct).where(
                TenantProduct.tenant_id == tenant_id,
                TenantProduct.is_deleted == 0,
                TenantProduct.status == 1,
            )
        )
        existing_products = existing_result.scalars().all()

        replace_active = bool(getattr(data, "replaceActive", False))
        if replace_active:
            # 替换语义：先软删其他生效授权，跳过时间冲突/空档期校验
            now = datetime.now()
            for ep in existing_products:
                still_active = ep.end_time is None or ep.end_time > now
                if still_active:
                    ep.is_deleted = 1
                    logger.info(
                        f"替换授权：软删租户 {tenant.tenant_code} 已有授权 "
                        f"id={ep.id} version={ep.version_code}"
                    )
            await db.flush()
            existing_products = []

        for ep in existing_products:
            if not start_time or not end_time or not ep.start_time or not ep.end_time:
                continue
            if start_time < ep.end_time and end_time > ep.start_time:
                raise BizException(
                    f"授权时间与已有授权冲突（{ep.version_code}: "
                    f"{ep.start_time.strftime('%Y-%m-%d')} ~ "
                    f"{ep.end_time.strftime('%Y-%m-%d')}）"
                )

        # 校验授权时间线不能存在空档期
        # 仅用「未来仍然有效（end_time > now）」的历史授权参与闭环检查；
        # 已过期的记录代表自然续约的合理断档，不应再约束新增授权的开始时间，
        # 否则当历史授权全部过期时，运营将永远无法补一条 startTime=now 的新授权。
        if start_time and end_time and not replace_active:
            now = datetime.now()
            future_periods = [
                (ep.start_time, ep.end_time)
                for ep in existing_products
                if ep.start_time and ep.end_time and ep.end_time > now
            ]
            all_periods = list(future_periods)
            all_periods.append((start_time, end_time))
            all_periods.sort(key=lambda x: x[0])
            for i in range(len(all_periods) - 1):
                cur_end = all_periods[i][1]
                nxt_start = all_periods[i + 1][0]
                if nxt_start > cur_end:
                    raise BizException(
                        f"授权时间存在空档期（"
                        f"{cur_end.strftime('%Y-%m-%d %H:%M:%S')} ~ "
                        f"{nxt_start.strftime('%Y-%m-%d %H:%M:%S')}），"
                        f"请确保新授权的开始时间紧接上一条有效授权的到期时间"
                    )

        # 创建授权记录
        product = TenantProduct(
            tenant_id=tenant_id,
            tenant_code=tenant.tenant_code,
            version_id=data.versionId,
            version_code=data.versionCode,
            start_time=start_time,
            end_time=end_time,
            grant_type=data.grantType,
            grant_remark=data.grantRemark,
            status=1,
        )
        db.add(product)

        if end_time:
            if tenant.expire_time is None or end_time > tenant.expire_time:
                tenant.expire_time = end_time

        # 过期客户开通版本时自动恢复
        if tenant.status == 3:
            tenant.status = 1
            logger.info(f"租户 {tenant.tenant_code} 已过期，开通新版本后自动恢复为正常状态")

        await db.flush()
        await db.refresh(product)
        logger.info(f"租户 {tenant.tenant_code} 已开通产品版本: {data.versionCode}")

        # 授权变更必须递增菜单版本戳，触发客户端重新拉取菜单
        tenant.menu_version = (tenant.menu_version or 0) + 1
        await db.flush()
        logger.info(
            f"租户 {tenant.tenant_code} menu_version 递增至 {tenant.menu_version}"
        )

        # 按版本功能清单按需创建租户库业务表
        try:
            await TenantService._ensure_version_tables(
                db, tenant.tenant_code, data.versionId
            )
        except Exception as e:
            logger.warning(
                f"租户 {tenant.tenant_code} 版本 {data.versionCode} 业务表创建失败（非致命）: {e}"
            )

        return product

    @staticmethod
    async def _ensure_version_tables(
        db: AsyncSession, tenant_code: str, version_id: int
    ) -> None:
        """根据版本功能清单，在租户库中按需创建业务表"""
        from app.modules.console.services.product.product_feature_service import ProductFeatureService

        import app.modules.client.models  # noqa: F401

        required_tables = await ProductFeatureService.get_required_tables_by_version_id(
            db, version_id
        )
        if not required_tables:
            return

        created = await db_manager.ensure_tenant_tables(tenant_code, required_tables)
        if created:
            logger.info(
                f"租户 {tenant_code} 版本开通，新建业务表: {created}"
            )

    @staticmethod
    async def remove_product(
        db: AsyncSession, tenant_id: int, product_id: int
    ) -> None:
        """取消产品授权"""
        result = await db.execute(
            select(TenantProduct).where(
                TenantProduct.id == product_id,
                TenantProduct.tenant_id == tenant_id,
                TenantProduct.is_deleted == 0,
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            raise BizException("授权记录不存在")

        product.is_deleted = 1
        await db.flush()

        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            return

        # 重新计算租户到期时间并同步状态
        now = datetime.now()
        remaining = await db.execute(
            select(TenantProduct).where(
                TenantProduct.tenant_id == tenant_id,
                TenantProduct.is_deleted == 0,
                TenantProduct.status == 1,
            )
        )
        remaining_products = remaining.scalars().all()

        active_products = [
            p for p in remaining_products
            if p.end_time is None or p.end_time > now
        ]

        if not active_products:
            tenant.expire_time = None
            if tenant.status == 1:
                tenant.status = 3
                logger.info(f"租户 {tenant.tenant_code} 已无有效授权，状态设为已过期")
        else:
            max_end = None
            for p in active_products:
                if p.end_time and (max_end is None or p.end_time > max_end):
                    max_end = p.end_time
            tenant.expire_time = max_end

        # 授权取消必须递增菜单版本戳，触发客户端重新拉取菜单
        tenant.menu_version = (tenant.menu_version or 0) + 1
        await db.flush()
        logger.info(
            f"租户 {tenant.tenant_code} 取消授权后 menu_version 递增至 {tenant.menu_version}"
        )

    # ============================================================
    # 过期检查
    # ============================================================

    @staticmethod
    async def check_expirations(db: AsyncSession) -> int:
        """
        检查过期授权 + 反范式字段自愈，返回受影响数量。

        以 sys_tenant_product 为唯一权威，强制把 sys_tenant.status / expire_time 拉齐：
        1. status=1 但已无任何有效授权 → status=3，expire_time=None
        2. status=3 但已出现新的有效授权（含手工 SQL 改 sys_tenant_product 的场景）
           → status=1，expire_time=有效授权的最晚 end_time（None 表示永久）
        3. status=1 且仍有有效授权 → 仅同步 expire_time（修正商业版到期时间漂移）

        因此「直接改 sys_tenant_product 后客户列表 / 当前版本不刷新」的问题
        在 30 秒级定时任务下会自动收敛；如需立即生效，运营同样可以手工触发本接口。
        """
        from sqlalchemy import or_
        now = datetime.now()
        affected = 0

        # 候选集：所有未删除租户。少量循环成本可控；
        # 即便上千租户也比直接改 SQL 出错的人工成本低。
        result = await db.execute(
            select(Tenant).where(Tenant.is_deleted == 0)
        )
        tenants = list(result.scalars().all())

        for tenant in tenants:
            prod_result = await db.execute(
                select(TenantProduct).where(
                    TenantProduct.tenant_id == tenant.id,
                    TenantProduct.is_deleted == 0,
                    TenantProduct.status == 1,
                    or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > now),
                )
            )
            active_products = list(prod_result.scalars().all())

            new_status = tenant.status
            new_expire = tenant.expire_time

            if active_products:
                if any(p.end_time is None for p in active_products):
                    new_expire = None
                else:
                    new_expire = max(p.end_time for p in active_products)
                if tenant.status == 3:
                    new_status = 1
                    logger.info(
                        f"租户 {tenant.tenant_code} 出现新的有效授权"
                        f"（{[(p.version_code, p.end_time) for p in active_products]}），"
                        f"status 由 3 自动恢复为 1"
                    )
            else:
                new_expire = None
                if tenant.status == 1:
                    new_status = 3
                    logger.info(
                        f"租户 {tenant.tenant_code} 已无有效授权，status 自动设为 3"
                    )

            changed = False
            if new_status != tenant.status:
                tenant.status = new_status
                changed = True
            if new_expire != tenant.expire_time:
                tenant.expire_time = new_expire
                changed = True
            if changed:
                # 任何 status / expire_time 变化都意味着客户端能见菜单可能改变，
                # 一并递增 menu_version 触发客户端刷新。
                tenant.menu_version = (tenant.menu_version or 0) + 1
                affected += 1

        await db.flush()
        if affected:
            logger.info(f"check_expirations 自愈 {affected} 个租户的 status/expire_time")
        return affected
