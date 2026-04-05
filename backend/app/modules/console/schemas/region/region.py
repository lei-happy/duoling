"""
Console 端地区数据 Schemas
操作平台库 sys_regions，字段名对齐前端 TypeScript 模型
"""

from typing import Optional
from pydantic import BaseModel


class RegionCreate(BaseModel):
    model_config = {"extra": "ignore"}

    name: str
    shortName: Optional[str] = None
    pcode: Optional[int] = None
    level: int = 1
    sortOrder: int = 0
    status: int = 1


class RegionUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    name: Optional[str] = None
    shortName: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None


class RegionOut(BaseModel):
    code: int
    name: str
    shortName: Optional[str] = None
    pcode: Optional[int] = None
    level: int
    sortOrder: int
    status: int
    createTime: Optional[str] = None
    hasChildren: bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, has_children: bool = False) -> "RegionOut":
        return cls(
            code=m.code,
            name=m.name,
            shortName=m.short_name,
            pcode=m.pcode,
            level=m.level,
            sortOrder=m.sort_order,
            status=m.status,
            createTime=(
                m.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if m.created_at else None
            ),
            hasChildren=has_children,
        )
