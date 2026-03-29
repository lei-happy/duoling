"""
企业端员工管理 Schemas
字段名对齐前端 TypeScript 模型（userId / nickname / organizationId 等）
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BizUserCreate(BaseModel):
    model_config = {"extra": "ignore"}

    phone: str
    password: str = "123456"
    nickname: Optional[str] = None
    realName: Optional[str] = None
    email: Optional[str] = None
    sex: Optional[str] = None
    organizationId: Optional[int] = None
    userType: int = 2
    roleIds: Optional[List[int]] = None
    status: int = 0
    introduction: Optional[str] = None


class BizUserUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    userId: int
    nickname: Optional[str] = None
    realName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[str] = None
    organizationId: Optional[int] = None
    userType: Optional[int] = None
    roleIds: Optional[List[int]] = None
    status: Optional[int] = None
    introduction: Optional[str] = None


class BizUserOut(BaseModel):
    userId: int
    phone: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[str] = None
    sexName: Optional[str] = None
    organizationId: Optional[int] = None
    organizationName: Optional[str] = None
    userType: int
    status: int
    introduction: Optional[str] = None
    createTime: Optional[str] = None
    roles: Optional[list] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, roles=None, dept_name: Optional[str] = None) -> "BizUserOut":
        gender_map = {0: None, 1: "男", 2: "女"}
        sex_val = gender_map.get(m.gender)
        return cls(
            userId=m.id,
            phone=m.phone,
            nickname=m.nickname or m.real_name,
            email=m.email,
            avatar=m.avatar,
            sex=sex_val,
            sexName=sex_val,
            organizationId=m.department_id,
            organizationName=dept_name,
            userType=m.user_type,
            status=m.status,
            introduction=m.remark,
            createTime=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
            roles=roles,
        )


class BizUserStatusUpdate(BaseModel):
    userId: int
    status: int
