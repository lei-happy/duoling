"""
企业自助注册 Schemas
"""

from typing import Optional
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """企业自助注册请求"""
    tenant_name: str               # 企业名称
    contact_person: str            # 联系人
    contact_phone: str             # 联系电话
    contact_email: Optional[str] = None  # 联系邮箱
    province: Optional[str] = None
    city: Optional[str] = None
    admin_username: Optional[str] = None  # 管理员用户名（默认自动生成）
    admin_password: Optional[str] = None  # 管理员密码（默认 123456）
    version_code: str = "basic"    # 申请的产品版本
    referrer_code: Optional[str] = None  # 推荐人企业编码（从URL参数 ?ref=xxx 传入）


class RegisterResponse(BaseModel):
    """企业自助注册响应"""
    tenant_code: str               # 分配的企业编码
    tenant_name: str               # 企业名称
    admin_username: str            # 管理员用户名
    message: str = "注册成功，请使用管理员账号登录客户端"
