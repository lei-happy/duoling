"""
租户管理服务
"""

from typing import Optional, Tuple, List
from datetime import datetime, timedelta

from sqlalchemy import select, func, exists, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.console.models.tenant import Tenant
from app.modules.console.models.tenant_product import TenantProduct
from app.modules.console.models.product_version import ProductVersion
from app.modules.console.models.user import User
from app.modules.console.models.user_tenant import UserTenant
from app.modules.console.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantOut, TenantListOut,
    TenantProductCreate, TenantProductOut,
    TenantFollowPoolUpdate,
)


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

    # ============================================================
    # 租户 CRUD
    # ============================================================

    @staticmethod
    async def create_tenant(
        db: AsyncSession, data: TenantCreate
    ) -> Tuple[Tenant, bool]:
        """
        创建新租户
        1. 生成租户编码
        2. 创建租户记录
        3. 创建租户独立数据库
        4. 关联或创建管理员账号

        返回: (tenant, is_existing_user)
            is_existing_user=True 表示管理员账号已存在（手机号已注册过）
        """
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
            remark=data.remark,
            source_channel=data.sourceChannel or "console",
            referrer_code=data.referrerCode,
        )
        db.add(tenant)
        await db.flush()

        # 创建租户独立数据库（仅 core 层表）
        try:
            import app.modules.client.models  # noqa: F401
            await db_manager.create_tenant_database(tenant_code)
            await TenantService._init_tenant_seed_data(
                tenant_code,
                admin_name=data.contactPerson or "管理员",
                admin_phone=data.contactPhone,
                admin_email=data.contactEmail,
            )
            tenant.db_initialized = 1
        except Exception as e:
            logger.error(f"创建租户数据库失败: {e}")
            tenant.db_initialized = 0

        # ---- 管理员账号：按手机号查找已有用户 ----
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
                f"手机号 {data.contactPhone} 已存在用户 {admin_user.username}，"
                f"复用该用户关联新企业 {tenant_code}"
            )
        else:
            # 新用户 —— 创建 User
            admin_user = User(
                username=f"admin_{tenant_code}",
                password=hash_password("123456"),
                real_name=data.contactPerson or "管理员",
                phone=data.contactPhone,
                email=data.contactEmail,
                user_type=2,  # 非平台管理员（具体角色由 UserTenant 决定）
                status=1,
                force_change_pwd=1,  # 首次登录强制修改密码
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
        else:
            db.add(UserTenant(
                user_id=admin_user.id,
                tenant_code=tenant_code,
                user_type=1,
                status=1,
            ))

        # 自动开通 basic 版本
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
                tenant_id=tenant.id,
                tenant_code=tenant_code,
                version_id=basic_version.id,
                version_code="basic",
                start_time=datetime.now(),
                end_time=None,
                status=1,
            )
            db.add(basic_product)

        await db.flush()
        logger.info(f"新租户已创建: {tenant_code} - {data.tenantName}")

        return tenant, is_existing_user

    @staticmethod
    async def _init_tenant_seed_data(
        tenant_code: str,
        admin_name: str = "管理员",
        admin_phone: Optional[str] = None,
        admin_email: Optional[str] = None,
    ) -> None:
        """
        在租户库中插入种子数据：默认角色、部门、管理员及关联。
        通过平台库同步地区数据到 biz_region。
        """
        from app.modules.client.models.biz_role import BizRole
        from app.modules.client.models.biz_department import BizDepartment
        from app.modules.client.models.biz_user import BizUser
        from app.modules.client.models.biz_user_role import BizUserRole

        engine = db_manager._get_or_create_tenant_engine(tenant_code)
        session_factory = db_manager._tenant_session_factories[tenant_code]

        async with session_factory() as session:
            try:
                # 默认角色
                roles = [
                    BizRole(role_code="admin", role_name="管理员", sort_order=0, status=1),
                    BizRole(role_code="operator", role_name="操作员", sort_order=10, status=1),
                    BizRole(role_code="driver", role_name="驾驶员", sort_order=20, status=1),
                ]
                session.add_all(roles)
                await session.flush()

                # 默认部门
                hq = BizDepartment(parent_id=0, dept_name="总公司", dept_code="HQ", sort_order=0, status=1)
                session.add(hq)
                await session.flush()
                sub_depts = [
                    BizDepartment(parent_id=hq.id, dept_name="运营部", dept_code="OP", sort_order=0, status=1),
                    BizDepartment(parent_id=hq.id, dept_name="车队部", dept_code="FL", sort_order=10, status=1),
                    BizDepartment(parent_id=hq.id, dept_name="财务部", dept_code="FI", sort_order=20, status=1),
                ]
                session.add_all(sub_depts)
                await session.flush()

                # 管理员用户
                admin_user = BizUser(
                    username=f"admin_{tenant_code}",
                    password=hash_password("123456"),
                    real_name=admin_name,
                    phone=admin_phone,
                    email=admin_email,
                    user_type=1,
                    department=hq.dept_name,
                    status=1,
                )
                session.add(admin_user)
                await session.flush()

                # 管理员-角色关联
                admin_role = roles[0]
                user_role = BizUserRole(user_id=admin_user.id, role_id=admin_role.id)
                session.add(user_role)

                await session.commit()
                logger.info(f"租户 {tenant_code} 种子数据已初始化")
            except Exception as e:
                await session.rollback()
                logger.error(f"租户 {tenant_code} 种子数据初始化失败: {e}")
                raise

        # 同步地区数据（从平台 sys_regions 到租户 biz_region）
        try:
            await TenantService._sync_region_data(tenant_code)
        except Exception as e:
            logger.warning(f"租户 {tenant_code} 地区数据同步失败（非致命）: {e}")

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

            # 构建 WHERE 条件：仅同步未删除的地区记录
            where_clause = ""
            if "is_deleted" in source_cols:
                where_clause = " WHERE `is_deleted` = 0"

            insert_sql = (
                f"INSERT INTO biz_region ({', '.join(target_cols)}) "
                f"SELECT {', '.join(source_exprs)} "
                f"FROM `{platform_db}`.sys_regions{where_clause}"
            )
            logger.info(f"地区同步 SQL: {insert_sql}")
            await conn.execute(text(insert_sql))

        logger.info(f"租户 {tenant_code} 地区数据已从平台同步")

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
            has_basic_active = TenantService._active_product_exists(version_code_filter="basic")
            has_paid_active = TenantService._active_product_exists(exclude_basic=True)
            query = query.where(Tenant.status == 1, has_basic_active, ~has_paid_active)
        elif lifecycle == "follow_up":
            query = query.where(Tenant.in_follow_pool == 1)
        elif lifecycle == "paid":
            has_paid_active = TenantService._active_product_exists(exclude_basic=True)
            query = query.where(Tenant.status == 1, has_paid_active)
            if version_code:
                version_cond = TenantService._active_product_exists(version_code_filter=version_code)
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

        return {
            "list": [TenantListOut.from_model(t).model_dump() for t in items],
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

        has_basic_active = TenantService._active_product_exists(version_code_filter="basic")
        has_paid_active = TenantService._active_product_exists(exclude_basic=True)

        new_q = base.where(Tenant.status == 1, Tenant.created_at >= cutoff)
        trial_q = base.where(Tenant.status == 1, has_basic_active, ~has_paid_active)
        follow_q = base.where(Tenant.in_follow_pool == 1)
        paid_q = base.where(Tenant.status == 1, has_paid_active)
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

        # 检查是否已授权相同版本
        existing = await db.execute(
            select(TenantProduct).where(
                TenantProduct.tenant_id == tenant_id,
                TenantProduct.version_id == data.versionId,
                TenantProduct.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException("该产品版本已授权，请勿重复开通")

        # 解析时间
        start_time = None
        end_time = None
        if data.startTime:
            start_time = datetime.strptime(data.startTime, "%Y-%m-%d %H:%M:%S")
        if data.endTime:
            end_time = datetime.strptime(data.endTime, "%Y-%m-%d %H:%M:%S")

        # 创建授权记录
        product = TenantProduct(
            tenant_id=tenant_id,
            tenant_code=tenant.tenant_code,
            version_id=data.versionId,
            version_code=data.versionCode,
            start_time=start_time,
            end_time=end_time,
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
        from app.modules.console.services.product_feature_service import ProductFeatureService

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

        await db.flush()

    # ============================================================
    # 过期检查
    # ============================================================

    @staticmethod
    async def check_expirations(db: AsyncSession) -> int:
        """检查过期授权，更新客户状态，返回受影响数量"""
        now = datetime.now()
        affected = 0

        # 查找 status=1 且 expire_time 已过期的客户
        result = await db.execute(
            select(Tenant).where(
                Tenant.is_deleted == 0,
                Tenant.status == 1,
                Tenant.expire_time.isnot(None),
                Tenant.expire_time < now,
            )
        )
        tenants = result.scalars().all()

        for tenant in tenants:
            # 检查是否还有其他有效授权
            prod_result = await db.execute(
                select(TenantProduct).where(
                    TenantProduct.tenant_id == tenant.id,
                    TenantProduct.is_deleted == 0,
                    TenantProduct.status == 1,
                    or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > now),
                )
            )
            active_products = prod_result.scalars().all()
            has_active_basic = any(p.version_code == "basic" for p in active_products)
            has_active_paid = any(p.version_code != "basic" for p in active_products)

            if not has_active_paid and has_active_basic:
                # 仅剩 basic 有效 → 客户回到免费体验，清空 expire_time
                tenant.expire_time = None
                affected += 1
                logger.info(f"租户 {tenant.tenant_code} 付费授权已过期，回退为免费体验")
            elif not active_products:
                # 无任何有效授权 → 设为已过期
                tenant.status = 3
                affected += 1
                logger.info(f"租户 {tenant.tenant_code} 所有授权已过期，状态设为已过期")

        await db.flush()
        return affected
