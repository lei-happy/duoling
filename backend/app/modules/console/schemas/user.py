"""
用户管理 Schemas
字段名对齐前端 EleAdminPlus User 接口（camelCase）
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class UserRoleItem(BaseModel):
    """用户关联的角色"""
    roleId: int
    roleCode: str
    roleName: str


class UserOut(BaseModel):
    """用户输出"""
    userId: int
    phone: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[str] = None
    email: Optional[str] = None
    status: Optional[int] = None
    organizationId: Optional[int] = None
    organizationName: Optional[str] = None
    roles: List[UserRoleItem] = []
    createTime: Optional[str] = None


class UserCreate(BaseModel):
    """新增用户"""
    phone: str
    password: Optional[str] = "123456"
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[str] = None
    email: Optional[str] = None
    organizationId: Optional[int] = None
    roles: Optional[List[int]] = None
    status: int = 0


class UserUpdate(BaseModel):
    """修改用户"""
    userId: int
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[str] = None
    email: Optional[str] = None
    organizationId: Optional[int] = None
    roles: Optional[List[int]] = None
    status: Optional[int] = None


class UserStatusUpdate(BaseModel):
    """修改用户状态"""
    userId: int
    status: int
