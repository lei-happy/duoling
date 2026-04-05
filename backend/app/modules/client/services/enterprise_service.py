"""
企业管理服务
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AuthException
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.tenant.tenant_product import TenantProduct
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.client.schemas.enterprise import (
    EnterpriseInfoOut, VersionInfo, UpdateSystemNameRequest,
)


class EnterpriseService:
    """企业管理服务"""

    @staticmethod
    async def get_enterprise_info(
        db: AsyncSession, tenant_code: str
    ) -> EnterpriseInfoOut:
        """获取企业信息及当前版本"""
        result = await db.execute(
            select(Tenant).where(
                Tenant.tenant_code == tenant_code,
                Tenant.is_deleted == 0,
            )
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise AuthException("企业信息不存在")

        version_info = await EnterpriseService._get_version_info(db, tenant_code)

        return EnterpriseInfoOut(
            tenantName=tenant.tenant_name,
            systemName=tenant.system_name,
            contactPerson=tenant.contact_person,
            contactPhone=tenant.contact_phone,
            version=version_info,
        )

    @staticmethod
    async def _get_version_info(
        db: AsyncSession, tenant_code: str
    ) -> Optional[VersionInfo]:
        """获取企业当前有效的版本信息"""
        from sqlalchemy import or_

        now = datetime.now()
        tp_result = await db.execute(
            select(TenantProduct).where(
                TenantProduct.tenant_code == tenant_code,
                TenantProduct.is_deleted == 0,
                TenantProduct.status == 1,
                or_(
                    TenantProduct.end_time.is_(None),
                    TenantProduct.end_time > now,
                ),
            ).order_by(TenantProduct.created_at.desc()).limit(1)
        )
        tenant_product = tp_result.scalar_one_or_none()
        if not tenant_product:
            return None

        pv_result = await db.execute(
            select(ProductVersion).where(
                ProductVersion.id == tenant_product.version_id,
                ProductVersion.is_deleted == 0,
            )
        )
        product_version = pv_result.scalar_one_or_none()
        if not product_version:
            return None

        return VersionInfo(
            versionName=product_version.version_name,
            versionCode=product_version.version_code,
            maxUsers=product_version.max_users,
            maxVehicles=product_version.max_vehicles,
            startTime=tenant_product.start_time,
            endTime=tenant_product.end_time,
        )

    @staticmethod
    async def update_system_name(
        db: AsyncSession,
        tenant_code: str,
        user_id: int,
        request: UpdateSystemNameRequest,
    ) -> None:
        """更新系统自定义名称（仅租户管理员可操作）"""
        ut_result = await db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user_id,
                UserTenant.tenant_code == tenant_code,
                UserTenant.is_deleted == 0,
            )
        )
        ut = ut_result.scalar_one_or_none()
        if not ut or ut.user_type != 1:
            raise AuthException("仅企业管理员可修改系统名称")

        result = await db.execute(
            select(Tenant).where(
                Tenant.tenant_code == tenant_code,
                Tenant.is_deleted == 0,
            )
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise AuthException("企业信息不存在")

        tenant.system_name = request.systemName
        await db.commit()
