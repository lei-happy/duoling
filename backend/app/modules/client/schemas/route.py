"""
路线管理 Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RouteRegionPointOut(BaseModel):
    regionId: int
    name: str
    longitude: float
    latitude: float


class RouteDrivingMetricsOut(BaseModel):
    distanceKm: float
    estimatedHours: float
    origin: RouteRegionPointOut
    destination: RouteRegionPointOut
    polylinePath: List[List[float]] = Field(
        default_factory=list,
        description="路线折线 [[lng, lat], ...]",
    )
    strategy: int = 34
    source: str = "amap_v5_driving"


class RouteCreate(BaseModel):
    """新建：编码与默认名称由后端生成；起终点必填行政区 id。"""

    routeName: Optional[str] = Field(None, description="可选；为空则按起终点生成")
    originRegionId: int = Field(..., description="出发地 biz_region.id")
    destinationRegionId: int = Field(..., description="目的地 biz_region.id")
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    routePolyline: Optional[List[List[float]]] = Field(
        None, description="驾车路线折线 [[lng, lat], ...]"
    )
    remark: Optional[str] = None


class RouteUpdate(BaseModel):
    routeName: Optional[str] = None
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    routePolyline: Optional[List[List[float]]] = Field(
        None, description="驾车路线折线；起终点变更后应传新折线"
    )
    clearRoutePolyline: Optional[bool] = Field(
        None, description="为 true 时清空已存折线"
    )
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
    polylinePath: List[List[float]] = Field(default_factory=list)
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "RouteOut":
        from app.common.route_polyline import decode_route_polyline

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
            polylinePath=decode_route_polyline(getattr(m, "route_polyline", None)),
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
