"""
忘记密码接口（预留）
当前版本仅返回联系管理员提示，后续接入短信验证码后可自助重置
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.modules.console.models.user import User
from sqlalchemy import select

router = APIRouter()


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    phone: str = Field(description="注册手机号")


class ForgotPasswordResponse(BaseModel):
    """忘记密码响应"""
    phone_exists: bool = False
    message: str = ""


@router.post("")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    忘记密码
    当前版本：检测手机号是否存在，返回联系管理员提示
    后续版本：发送短信验证码，支持自助重置密码
    """
    # 检查手机号是否存在
    result = await db.execute(
        select(User).where(
            User.phone == data.phone,
            User.is_deleted == 0,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        return success(data=ForgotPasswordResponse(
            phone_exists=False,
            message="该手机号尚未注册，请先注册企业账号",
        ).model_dump())

    return success(data=ForgotPasswordResponse(
        phone_exists=True,
        message="请联系您的企业管理员或系统管理员重置密码。后续版本将支持手机短信验证码自助找回。",
    ).model_dump())
