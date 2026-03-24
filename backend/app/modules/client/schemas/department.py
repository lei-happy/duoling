"""
组织架构/部门 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    parentId: int = 0
    deptName: str
    deptCode: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    sortOrder: int = 0
    remark: Optional[str] = None


class DepartmentUpdate(BaseModel):
    parentId: Optional[int] = None
    deptName: Optional[str] = None
    deptCode: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class DepartmentOut(BaseModel):
    id: int
    parentId: int
    deptName: str
    deptCode: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    sortOrder: int
    status: int
    remark: Optional[str] = None
    createdAt: datetime
    children: Optional[List["DepartmentOut"]] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "DepartmentOut":
        return cls(
            id=m.id,
            parentId=m.parent_id,
            deptName=m.dept_name,
            deptCode=m.dept_code,
            leader=m.leader,
            phone=m.phone,
            sortOrder=m.sort_order,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
