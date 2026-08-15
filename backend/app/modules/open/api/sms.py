"""
短信验证码开放接口
无需认证：发送验证码、验证码重置密码
"""

import re

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.common.exceptions import BizException
from app.modules.open.services.sms_service import SmsService, PURPOSE_TENANT_REGISTER

router = APIRouter()

_CN_MOBILE = re.compile(r"^1[3-9]\d{9}$")


class SmsSendRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(description="手机号")
    purpose: int = Field(
        description="用途 1-验证码登录 2-重置密码 4-官网企业注册"
    )
    app_type: str = Field(
        description="应用类型 console-管理后台 client-客户端 website-官网"
    )

    @field_validator("phone")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not _CN_MOBILE.match(v or ""):
            raise ValueError("请输入正确的手机号码")
        return v


class SmsResetPasswordRequest(BaseModel):
    """验证码重置密码请求"""
    phone: str = Field(description="手机号")
    code: str = Field(description="验证码")
    newPassword: str = Field(description="新密码", min_length=6)

    @field_validator("phone")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not _CN_MOBILE.match(v or ""):
            raise ValueError("请输入正确的手机号码")
        return v


@router.post("/send")
async def send_sms_code(
    data: SmsSendRequest,
    request: Request,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    发送短信验证码（当前版本仅落表，不发送真实短信）。
    返回值中包含 code 字段，开发阶段可直接使用；
    接入短信通道后将移除该返回字段。
    """
    # 官网自助注册已下线，这条通道只保留给承运商邀请激活（app_type=client）
    if data.purpose == PURPOSE_TENANT_REGISTER and data.app_type == "website":
        raise BizException(
            "开户已改为顾问协助办理，请在官网留下联系方式，我们 1 个工作日内回电。"
        )

    client_ip = request.client.host if request.client else None
    result = await SmsService.send_code(
        db, data.phone, data.purpose,
        app_type=data.app_type, client_ip=client_ip,
    )
    return success(data=result)


@router.post("/reset-password")
async def reset_password_by_sms(
    data: SmsResetPasswordRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """通过短信验证码重置密码"""
    await SmsService.reset_password_by_sms(db, data.phone, data.code, data.newPassword)
    return success(message="密码重置成功")
