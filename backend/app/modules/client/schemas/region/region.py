"""
地区数据 Schemas
字段名对齐前端 TypeScript 模型
"""

from typing import Optional
from pydantic import BaseModel


class RegionCreate(BaseModel):
    model_config = {"extra": "ignore"}

    name: str
    parentCode: Optional[str] = None
    sortOrder: int = 0
    status: int = 1
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class RegionUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    name: Optional[str] = None
    parentCode: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class RegionOut(BaseModel):
    regionId: int
    code: str
    name: str
    parentCode: Optional[str] = None
    level: int
    sortOrder: int
    status: int
    source: int
    createdBy: Optional[int] = None
    createTime: Optional[str] = None
    hasChildren: bool = False
    longitude: Optional[float] = None
    latitude: Optional[float] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, has_children: bool = False) -> "RegionOut":
        return cls(
            regionId=m.id,
            code=m.code,
            name=m.name,
            parentCode=m.parent_code,
            level=m.level,
            sortOrder=m.sort_order,
            status=m.status,
            source=m.source,
            createdBy=m.created_by,
            createTime=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
            hasChildren=has_children,
            longitude=float(m.longitude) if m.longitude is not None else None,
            latitude=float(m.latitude) if m.latitude is not None else None,
        )
