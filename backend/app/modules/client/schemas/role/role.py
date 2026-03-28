"""
企业端角色管理 Schemas
字段名对齐前端 TypeScript 模型（roleId / roleName / roleCode 等）
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BizRoleCreate(BaseModel):
    model_config = {"extra": "ignore"}

    roleCode: str
    roleName: str
    comments: Optional[str] = None


class BizRoleUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    roleId: int
    roleName: Optional[str] = None
    roleCode: Optional[str] = None
    comments: Optional[str] = None


class BizRoleOut(BaseModel):
    roleId: int
    roleCode: str
    roleName: str
    comments: Optional[str] = None
    createTime: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "BizRoleOut":
        return cls(
            roleId=m.id,
            roleCode=m.role_code,
            roleName=m.role_name,
            comments=m.remark,
            createTime=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        )


class BizRoleMenuAssign(BaseModel):
    menuIds: List[int]
