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
        1. 创建租户（复用 TenantService，自动检测手机号是否已注册）
        2. 自动激活为正常状态（免费版）
        3. 返回注册结果（区分新用户 / 已有用户）
        """
        # 确定来源渠道
        source_channel = "referral" if data.referrer_code else "website"

        # 使用 TenantService 创建租户（会自动创建数据库、检测/创建管理员账号）
        tenant_data = TenantCreate(
            tenantName=data.tenant_name,
            contactPerson=data.contact_person,
            contactPhone=data.contact_phone,
            contactEmail=data.contact_email,
            province=data.province,
            city=data.city,
            remark="官网自助注册 - 免费版",
            sourceChannel=source_channel,
            referrerCode=data.referrer_code,
        )
        tenant, is_existing_user = await TenantService.create_tenant(db, tenant_data)

        # 自动激活：官网注册直接设为正常状态，用户可立即登录
        tenant.status = 1
        await db.flush()

        admin_username = f"admin_{tenant.tenant_code}"
        logger.info(
            f"企业自助注册成功: {tenant.tenant_code} - {data.tenant_name} "
            f"(渠道: {source_channel}, 已自动激活, 已有用户: {is_existing_user})"
        )

        # 根据是否已有用户返回不同提示
        if is_existing_user:
            message = "注册成功，该手机号已注册过账号，请使用已有密码登录"
        else:
            message = "注册成功，默认密码为 123456，首次登录后请修改密码"

        return RegisterResponse(
            tenant_code=tenant.tenant_code,
            tenant_name=tenant.tenant_name,
            admin_username=admin_username,
            admin_phone=data.contact_phone,
            is_existing_user=is_existing_user,
            message=message,
        )
