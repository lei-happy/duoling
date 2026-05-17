"""
路线管理 Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RouteCreate(BaseModel):
    """新建：编码与默认名称由后端生成；起终点必填行政区 id。"""

    routeName: Optional[str] = Field(None, description="可选；为空则按起终点生成")
    originRegionId: int = Field(..., description="出发地 biz_region.id")
    destinationRegionId: int = Field(..., description="目的地 biz_region.id")
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    remark: Optional[str] = None


class RouteUpdate(BaseModel):
    routeName: Optional[str] = None
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class RouteOut(BaseModel):
    id: int
    routeName: str
    routeCode: Optional[str] = None
    origin: str
    destination: str
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    originCode: Optional[str] = None
    destinationCode: Optional[str] = None
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    waypoints: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "RouteOut":
        return cls(
            id=m.id,
            routeName=m.route_name,
            routeCode=m.route_code,
            origin=m.origin,
            destination=m.destination,
            originRegionId=getattr(m, "origin_region_id", None),
            destinationRegionId=getattr(m, "destination_region_id", None),
            originCode=getattr(m, "origin_code", None),
            destinationCode=getattr(m, "destination_code", None),
            distance=float(m.distance) if m.distance is not None else None,
            estimatedHours=float(m.estimated_hours)
            if m.estimated_hours is not None
            else None,
            waypoints=m.waypoints,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
