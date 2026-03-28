"""
组织架构/部门 Schemas
字段名对齐前端 TypeScript 模型（organizationId / organizationName 等）
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    model_config = {"extra": "ignore"}

    parentId: int = 0
    organizationName: str
    organizationCode: Optional[str] = None
    organizationType: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    sortNumber: int = 0
    comments: Optional[str] = None


class DepartmentUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    organizationId: int
    parentId: Optional[int] = None
    organizationName: Optional[str] = None
    organizationCode: Optional[str] = None
    organizationType: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    sortNumber: Optional[int] = None
    status: Optional[int] = None
    comments: Optional[str] = None


class DepartmentOut(BaseModel):
    organizationId: int
    parentId: int
    organizationName: str
    organizationCode: Optional[str] = None
    organizationType: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    sortNumber: int
    status: int
    comments: Optional[str] = None
    createTime: Optional[str] = None
    children: Optional[List["DepartmentOut"]] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "DepartmentOut":
        return cls(
            organizationId=m.id,
            parentId=m.parent_id,
            organizationName=m.dept_name,
            organizationCode=m.dept_code,
            organizationType=m.dept_type,
            leader=m.leader,
            phone=m.phone,
            sortNumber=m.sort_order,
            status=m.status,
            comments=m.remark,
            createTime=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        )
