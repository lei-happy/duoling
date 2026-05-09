"""
当前登录用户接口（与运营前端路径约定：/user/me/*）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.auth.auth import ChangePasswordRequest
from app.modules.console.services.auth.auth_service import AuthService

router = APIRouter()


@router.put("/me/password")
async def change_my_password(
    data: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """修改当前登录用户密码（校验旧密码，不使用短信验证码）"""
    await AuthService.change_password(db, current_user.user_id, data)
    return success(message="密码修改成功")
