"""
客户端认证接口
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
async def client_login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    客户端登录
    需要提供 tenant_code + username + password
    """
    result = await AuthService.client_login(db, request)
    return success(data=result.model_dump())


@router.get("/user-info")
async def get_user_info(
    current_user: TokenData = Depends(get_current_user),
):
    """获取当前登录用户信息"""
    return success(data=current_user.model_dump())
