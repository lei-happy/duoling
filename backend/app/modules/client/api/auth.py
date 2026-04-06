"""
客户端认证接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_platform_db, get_current_user, get_tenant_db
from app.core.security import TokenData
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.console.schemas.auth.auth import (
    LoginRequest, SmsLoginRequest, LoginResponse, MultiTenantResponse,
    ChangePasswordRequest, RefreshTokenRequest,
    UpdateProfileRequest, UpdateThemeConfigRequest, SwitchTenantRequest,
)
from app.modules.console.services.auth.auth_service import AuthService

router = APIRouter()


@router.post("/login")
async def client_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    客户端登录（手机号 + 密码）
    当手机号对应多个企业时，返回企业选择列表
    """
    result = await AuthService.client_login(db, login_data)
    return success(data=result.model_dump())


@router.post("/sms-login")
async def client_sms_login(
    login_data: SmsLoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    客户端验证码登录
    当手机号对应多个企业时，返回企业选择列表
    """
    result = await AuthService.client_sms_login(
        db, login_data.phone, login_data.code, login_data.tenant_code
    )
    return success(data=result.model_dump())


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """刷新 Token"""
    result = await AuthService.refresh_token(db, request)
    return success(data=result.model_dump())


@router.get("/user-info")
async def get_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """获取当前登录用户信息（含角色、菜单/权限）"""
    user_info = await AuthService.get_user_info(
        db, current_user.user_id, app_type="client",
        tenant_code=current_user.tenant_code,
    )
    return success(data=user_info.model_dump())


@router.get("/user-tenants")
async def get_user_tenants(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """获取当前用户关联的所有有效租户列表"""
    tenants = await AuthService.get_user_tenants(db, current_user.user_id)
    return success(data=[t.model_dump() for t in tenants])


@router.post("/switch-tenant")
async def switch_tenant(
    request: SwitchTenantRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """切换到目标租户，返回新的 Token"""
    result = await AuthService.switch_tenant(db, current_user.user_id, request)
    return success(data=result.model_dump())


@router.put("/user")
async def update_profile(
    data: UpdateProfileRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
):
    """更新当前登录用户的个人资料"""
    result = await AuthService.update_profile(
        db, current_user.user_id, data, tenant_db=tenant_db,
    )
    return success(data=result)


@router.put("/password")
@operation_log(module="账号安全", action="修改密码", description="修改登录密码")
async def change_password(
    request: Request,
    data: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """修改密码（首次登录强制修改）"""
    await AuthService.change_password(db, current_user.user_id, data)
    return success(message="密码修改成功")


@router.put("/user-theme")
async def update_user_theme(
    request: UpdateThemeConfigRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """保存当前登录用户的主题配置"""
    await AuthService.update_theme_config(db, current_user.user_id, request)
    return success(message="保存成功")
