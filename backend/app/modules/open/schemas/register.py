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
    referrer_code: Optional[str] = None  # 推荐人企业编码（从URL参数 ?ref=xxx 传入）


class RegisterResponse(BaseModel):
    """企业自助注册响应"""
    tenant_code: str               # 分配的企业编码
    tenant_name: str               # 企业名称
    admin_username: str            # 管理员用户名
    admin_phone: str               # 管理员手机号（即联系电话，可用于登录）
    is_existing_user: bool = False  # 手机号是否已存在（True=老用户、False=新用户）
    message: str = "注册成功，默认密码为 123456，首次登录后请修改密码"
