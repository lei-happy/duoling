"""
租户管理服务
"""

from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.console.models.tenant import Tenant
from app.modules.console.models.tenant_product import TenantProduct
from app.modules.console.models.user import User
from app.modules.console.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantOut, TenantListOut,
    TenantProductCreate, TenantProductOut,
)


class TenantService:
    """租户管理服务"""

    # ============================================================
    # 租户 CRUD
    # ============================================================

    @staticmethod
    async def create_tenant(
        db: AsyncSession, data: TenantCreate
    ) -> Tenant:
        """
        创建新租户
        1. 生成租户编码
        2. 创建租户记录
        3. 创建租户独立数据库
        4. 创建租户管理员账号
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
            status=2,  # 待审核
            db_name=db_name,
            remark=data.remark,
            source_channel=data.sourceChannel or "console",
            referrer_code=data.referrerCode,
        )
        db.add(tenant)
        await db.flush()

        # 创建租户独立数据库
        try:
            # 确保 client models 已导入，以便 TenantBase.metadata 包含所有表
            import app.modules.client.models  # noqa: F401
            await db_manager.create_tenant_database(tenant_code)
            tenant.db_initialized = 1
        except Exception as e:
            logger.error(f"创建租户数据库失败: {e}")
            tenant.db_initialized = 0

        # 创建租户管理员账号
        admin_user = User(
            username=f"admin_{tenant_code}",
            password=hash_password("123456"),
            real_name=data.contactPerson or "管理员",
            phone=data.contactPhone,
            email=data.contactEmail,
            user_type=1,  # 租户管理员
            tenant_code=tenant_code,
            status=1,
            force_change_pwd=1,  # 首次登录强制修改密码
        )
        db.add(admin_user)

        await db.flush()
        logger.info(f"新租户已创建: {tenant_code} - {data.tenantName}")

        return tenant

    @staticmethod
    async def page_tenants(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
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
        """更新租户状态"""
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise BizException("租户不存在")
        tenant.status = status
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

        # 同步更新租户状态为正常 + 到期时间
        if tenant.status == 2:  # 待审核 -> 正常
            tenant.status = 1
        if end_time:
            # 取所有授权中最晚的到期时间作为租户到期时间
            if tenant.expire_time is None or end_time > tenant.expire_time:
                tenant.expire_time = end_time

        await db.flush()
        logger.info(f"租户 {tenant.tenant_code} 已开通产品版本: {data.versionCode}")
        return product

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

        # 重新计算租户到期时间
        remaining = await db.execute(
            select(TenantProduct).where(
                TenantProduct.tenant_id == tenant_id,
                TenantProduct.is_deleted == 0,
            )
        )
        remaining_products = remaining.scalars().all()
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if tenant:
            if not remaining_products:
                tenant.expire_time = None
            else:
                max_end = None
                for p in remaining_products:
                    if p.end_time and (max_end is None or p.end_time > max_end):
                        max_end = p.end_time
                tenant.expire_time = max_end
            await db.flush()
