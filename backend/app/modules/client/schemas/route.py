"""
路线管理 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RouteCreate(BaseModel):
    routeName: str
    routeCode: Optional[str] = None
    origin: str
    destination: str
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    waypoints: Optional[str] = None
    remark: Optional[str] = None


class RouteUpdate(BaseModel):
    routeName: Optional[str] = None
    routeCode: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance: Optional[float] = None
    estimatedHours: Optional[float] = None
    waypoints: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class RouteOut(BaseModel):
    id: int
    routeName: str
    routeCode: Optional[str] = None
    origin: str
    destination: str
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
            distance=float(m.distance) if m.distance is not None else None,
            estimatedHours=float(m.estimated_hours) if m.estimated_hours is not None else None,
            waypoints=m.waypoints,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
