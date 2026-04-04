"""
企业自助注册 Schemas
"""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


_CN_MOBILE = re.compile(r"^1[3-9]\d{9}$")


class RegisterPayload(BaseModel):
    """企业自助注册业务数据（持久化至注册任务，不含短信验证码）"""
    tenant_name: str
    contact_person: str
    contact_phone: str
    province: Optional[str] = None
    city: Optional[str] = None
    referrer_code: Optional[str] = None

    @field_validator("contact_phone")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not _CN_MOBILE.match(v or ""):
            raise ValueError("请输入正确的手机号码")
        return v


class RegisterSubmitRequest(RegisterPayload):
    """官网提交注册（含短信验证码，不入库）"""
    sms_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="短信验证码",
    )


class RegisterResponse(BaseModel):
    """企业自助注册结果（开户完成后）"""
    tenant_code: str               # 分配的企业编码
    tenant_name: str               # 企业名称
    admin_phone: str               # 管理员手机号（登录标识）
    is_existing_user: bool = False  # 手机号是否已存在（True=老用户、False=新用户）
    message: str = "注册成功，默认密码为 123456，首次登录后请修改密码"


class RegisterStartResponse(BaseModel):
    """提交异步注册后返回"""
    task_id: str = Field(..., description="轮询进度用的任务 ID")


class RegisterProgressOut(BaseModel):
    """注册任务进度查询"""
    status: str = Field(..., description="pending running success failed")
    current_step: str = ""
    message: str = ""
    percent: int = 0
    result: Optional[RegisterResponse] = None
    error_message: Optional[str] = None


class RegisterPhoneCheckOut(BaseModel):
    """官网校验手机号是否已在平台注册"""
    registered: bool = Field(..., description="true 表示已注册，应引导登录")
