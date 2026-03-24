"""
企业端员工管理 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BizUserCreate(BaseModel):
    username: str
    password: str = "123456"
    realName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: int = 0
    userType: int = 2
    department: Optional[str] = None
    departmentId: Optional[int] = None
    roleIds: Optional[List[int]] = None
    remark: Optional[str] = None


class BizUserUpdate(BaseModel):
    realName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[int] = None
    userType: Optional[int] = None
    department: Optional[str] = None
    departmentId: Optional[int] = None
    roleIds: Optional[List[int]] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class BizUserOut(BaseModel):
    id: int
    username: str
    realName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: int
    userType: int
    department: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime
    roles: Optional[list] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, roles=None) -> "BizUserOut":
        return cls(
            id=m.id,
            username=m.username,
            realName=m.real_name,
            phone=m.phone,
            email=m.email,
            avatar=m.avatar,
            gender=m.gender,
            userType=m.user_type,
            department=m.department,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
            roles=roles,
        )


class BizUserResetPassword(BaseModel):
    userId: int
    newPassword: str = "123456"
