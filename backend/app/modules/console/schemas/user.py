"""
用户管理 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    """创建用户"""
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: int = 0
    user_type: int = 1
    tenant_code: Optional[str] = None
    role_ids: List[int] = []
    remark: Optional[str] = None


class UserUpdate(BaseModel):
    """更新用户"""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[int] = None
    status: Optional[int] = None
    role_ids: Optional[List[int]] = None
    remark: Optional[str] = None


class UserOut(BaseModel):
    """用户输出"""
    id: int
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: int
    user_type: int
    tenant_code: Optional[str] = None
    status: int
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []

    model_config = {"from_attributes": True}


class UpdatePasswordRequest(BaseModel):
    """修改密码"""
    old_password: str
    new_password: str
