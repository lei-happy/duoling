"""
企业自助注册 Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


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
