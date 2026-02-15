"""
客户端认证接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.auth import (
    LoginRequest, LoginResponse, MultiTenantResponse,
    ChangePasswordRequest,
)
from app.modules.console.services.auth_service import AuthService

router = APIRouter()


@router.post("/login")
async def client_login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    客户端登录
    支持手机号/用户名 + 密码登录
    当手机号对应多个企业时，返回企业选择列表
    """
    result = await AuthService.client_login(db, request)
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


@router.put("/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """修改密码（首次登录强制修改）"""
    await AuthService.change_password(db, current_user.user_id, request)
    return success(message="密码修改成功")
