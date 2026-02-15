"""
企业自助注册服务
"""

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.modules.console.services.tenant_service import TenantService
from app.modules.console.schemas.tenant import TenantCreate
from app.modules.open.schemas.register import RegisterRequest, RegisterResponse


class RegisterService:
    """企业自助注册服务"""

    @staticmethod
    async def register(db: AsyncSession, data: RegisterRequest) -> RegisterResponse:
        """
        企业自助注册
        1. 创建租户（复用 TenantService）
        2. 返回注册结果
        """
        # 确定来源渠道
        source_channel = "referral" if data.referrer_code else "website"

        # 使用 TenantService 创建租户（会自动创建数据库和管理员账号）
        tenant_data = TenantCreate(
            tenantName=data.tenant_name,
            contactPerson=data.contact_person,
            contactPhone=data.contact_phone,
            contactEmail=data.contact_email,
            province=data.province,
            city=data.city,
            remark=f"自助注册，申请版本: {data.version_code}",
            sourceChannel=source_channel,
            referrerCode=data.referrer_code,
        )
        tenant = await TenantService.create_tenant(db, tenant_data)

        admin_username = f"admin_{tenant.tenant_code}"
        logger.info(f"企业自助注册成功: {tenant.tenant_code} - {data.tenant_name} (渠道: {source_channel})")

        return RegisterResponse(
            tenant_code=tenant.tenant_code,
            tenant_name=tenant.tenant_name,
            admin_username=admin_username,
        )
