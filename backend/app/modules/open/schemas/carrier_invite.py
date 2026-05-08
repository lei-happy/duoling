"""
承运商邀请着陆页 / 激活 Schemas（开放接口）
"""

import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


_CN_MOBILE = re.compile(r"^1[3-9]\d{9}$")


class CarrierInviteInfoOut(BaseModel):
    """着陆页加载邀请信息（不含敏感字段）"""
    inviteCode: str
    sourceTenantName: str = Field(description="邀请方企业名（A 的 tenant_name）")
    expectedCarrierName: str = Field(description="A 录入的承运商名（着陆页默认企业名建议值）")
    invitePhoneMasked: str = Field(description="脱敏的被邀请手机号（前 3 后 4）")
    invitePath: str = Field(description="B / C1 / C2 / C3")
    status: int = Field(description="邀请当前状态")
    expiresAt: datetime
    expired: bool = Field(description="True 表示邀请已失效")
    userExisted: bool = Field(description="该手机号是否已注册 sys_user")


class CarrierInviteActivateRequest(BaseModel):
    """着陆页提交激活（路径 B）"""
    inviteCode: str = Field(description="邀请码")
    contactPhone: str = Field(description="被邀请人手机号（必须等于邀请记录里的手机号）")
    smsCode: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$",
                         description="短信验证码")
    realName: str = Field(description="真实姓名")
    tenantName: str = Field(description="自定义企业名称（默认值=expectedCarrierName，可改）")
    shortName: Optional[str] = None

    @field_validator("contactPhone")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not _CN_MOBILE.match(v or ""):
            raise ValueError("请输入正确的手机号码")
        return v


class CarrierInviteActivateResponse(BaseModel):
    """激活成功响应（用于直接登录）"""
    tenantCode: str
    tenantName: str
    versionCode: str
    accessToken: str
    refreshToken: Optional[str] = None
    message: str = "激活成功，已为您开通轻量版账号"
