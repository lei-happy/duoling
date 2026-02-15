"""
认证接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.auth import LoginRequest
from app.modules.console.services.auth_service import AuthService

router = APIRouter()


@router.post("/login")
async def platform_login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """平台管理后台登录"""
    result = await AuthService.platform_login(db, request)
    return success(data=result.model_dump())


@router.get("/user-info")
async def get_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """获取当前登录用户信息（含角色、菜单/权限）"""
    user_info = await AuthService.get_user_info(db, current_user.user_id)
    return success(data=user_info.model_dump())
