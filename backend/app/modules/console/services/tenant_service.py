"""
租户管理服务
"""

from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.console.models.tenant import Tenant
from app.modules.console.models.user import User
from app.modules.console.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    """租户管理服务"""

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
                Tenant.tenant_name == data.tenant_name,
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
            tenant_name=data.tenant_name,
            short_name=data.short_name,
            contact_person=data.contact_person,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            province=data.province,
            city=data.city,
            address=data.address,
            license_no=data.license_no,
            status=1,  # 直接启用
            db_name=db_name,
            remark=data.remark,
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
            real_name=data.contact_person or "管理员",
            phone=data.contact_phone,
            email=data.contact_email,
            user_type=1,  # 租户管理员
            tenant_code=tenant_code,
            status=1,
        )
        db.add(admin_user)

        await db.flush()
        logger.info(f"新租户已创建: {tenant_code} - {data.tenant_name}")

        return tenant

    @staticmethod
    async def get_tenant_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[Tenant], int]:
        """获取租户列表（分页）"""
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
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页数据
        query = query.order_by(Tenant.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

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
        db: AsyncSession, tenant_id: int, data: TenantUpdate
    ) -> Optional[Tenant]:
        """更新租户信息"""
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise BizException("租户不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)

        await db.flush()
        return tenant

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: int) -> bool:
        """删除租户（软删除）"""
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise BizException("租户不存在")

        tenant.is_deleted = 1
        await db.flush()
        return True
