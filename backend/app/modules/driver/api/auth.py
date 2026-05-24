"""
驾驶员认证接口

- ``POST /auth/login``         手机号 + 密码
- ``POST /auth/sms-login``     手机号 + 验证码
- ``POST /auth/refresh``       Token 刷新（复用 AuthService.refresh_token）
- ``GET  /auth/user-info``     司机详情 + 角色 + 权限 + 当前 biz_driver.id
- ``GET  /auth/user-tenants``  当前手机号可见的驾驶员企业列表
- ``POST /auth/switch-tenant`` 切换企业，签发新 Token
- ``PUT  /auth/password``      修改密码（复用 AuthService.change_password）
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import (
    get_current_user,
    get_platform_db,
    get_tenant_db,
)
from app.core.security import TokenData
from app.modules.console.schemas.auth.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    SmsLoginRequest,
    SwitchTenantRequest,
)
from app.modules.console.services.auth.auth_service import AuthService
from app.modules.driver.services.driver_auth_service import DriverAuthService
from app.modules.driver.services.driver_context import get_current_driver

router = APIRouter()


@router.post("/login", summary="驾驶员密码登录")
async def driver_login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    手机号 + 密码登录（仅 user_type=3 的驾驶员账号可通过）。
    - 单企业：直接返回 access/refresh token
    - 多企业：返回 needSelectTenant + tenants 列表
    """
    result = await DriverAuthService.driver_login(db, payload)
    return success(data=result.model_dump())


@router.post("/sms-login", summary="驾驶员验证码登录")
async def driver_sms_login(
    payload: SmsLoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    result = await DriverAuthService.driver_sms_login(
        db, payload.phone, payload.code, payload.tenant_code
    )
    return success(data=result.model_dump())


@router.post("/refresh", summary="刷新 Token")
async def driver_refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    result = await AuthService.refresh_token(db, payload)
    return success(data=result.model_dump())


@router.get("/user-tenants", summary="可登录企业列表")
async def list_user_tenants(
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    items = await DriverAuthService.list_driver_tenants(db, current_user.user_id)
    return success(data=[i.model_dump() for i in items])


@router.post("/switch-tenant", summary="切换企业")
async def switch_tenant(
    payload: SwitchTenantRequest,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    result = await DriverAuthService.switch_tenant(
        db, current_user.user_id, payload
    )
    return success(data=result.model_dump())


@router.put("/password", summary="修改密码")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    await AuthService.change_password(db, current_user.user_id, payload)
    return success(message="密码已修改")


@router.get("/user-info", summary="司机信息 + 角色 + 权限 + driver_id")
async def get_user_info(
    request: Request,
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    在 client 端的 ``get_user_info`` 基础上补充以下司机维度字段：
    - driverId / driverCode（当前企业内 biz_driver.id / driver_code）
    - forceChangePwd（取自 sys_user.force_change_pwd；首次登录强制改密的标记）
    """
    from sqlalchemy import select as _select
    from app.modules.console.models.system.user import User as _User

    base = await AuthService.get_user_info(
        platform_db,
        current_user.user_id,
        app_type="client",
        tenant_code=current_user.tenant_code,
    )
    ctx = await get_current_driver(tenant_db, current_user)
    u_res = await platform_db.execute(
        _select(_User).where(_User.id == current_user.user_id)
    )
    sys_user = u_res.scalar_one_or_none()
    force_flag = int(getattr(sys_user, "force_change_pwd", 0) or 0)

    extra = {
        "driverId": ctx.driver_id,
        "driverCode": ctx.driver.driver_code,
        "userId": base.userId,
        "phone": base.phone,
        "realName": ctx.driver.name or base.nickname,
        "avatar": ctx.driver.avatar or base.avatar,
        "tenantCode": current_user.tenant_code,
        "tenantName": base.tenantName,
        "userType": base.userType,
        "menuVersion": base.menuVersion,
        "forceChangePwd": force_flag,
        "roles": [r.roleCode for r in base.roles],
        "permissions": [m.authority for m in base.authorities if m.authority],
        "menus": [m.model_dump() for m in base.authorities],
    }
    return success(data=extra)
