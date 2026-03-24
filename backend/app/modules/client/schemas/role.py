"""
企业端角色管理 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BizRoleCreate(BaseModel):
    roleCode: str
    roleName: str
    sortOrder: int = 0
    remark: Optional[str] = None


class BizRoleUpdate(BaseModel):
    roleName: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class BizRoleOut(BaseModel):
    id: int
    roleCode: str
    roleName: str
    sortOrder: int
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "BizRoleOut":
        return cls(
            id=m.id,
            roleCode=m.role_code,
            roleName=m.role_name,
            sortOrder=m.sort_order,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )


class BizRoleMenuAssign(BaseModel):
    """分配角色菜单"""
    roleId: int
    menuIds: List[int]
