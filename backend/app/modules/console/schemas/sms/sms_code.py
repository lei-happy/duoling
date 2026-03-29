"""
短信验证码记录 Schemas（管理后台查看）
字段名对齐前端 camelCase
"""

from typing import Optional

from pydantic import BaseModel


class SmsCodeOut(BaseModel):
    """短信验证码记录输出"""
    id: int
    phone: str
    code: str
    purpose: int
    status: int
    expireAt: str
    clientIp: Optional[str] = None
    createdAt: str
