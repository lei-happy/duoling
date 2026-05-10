"""
驾驶员常跑线路 Schemas
"""

from typing import List
from pydantic import BaseModel


class DriverRouteCreate(BaseModel):
    originCode: str
    originName: str
    destCode: str
    destName: str


class DriverRouteOut(BaseModel):
    id: int
    driverId: int
    originCode: str
    originName: str
    destCode: str
    destName: str
    status: int

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "DriverRouteOut":
        return cls(
            id=m.id,
            driverId=m.driver_id,
            originCode=m.origin_code,
            originName=m.origin_name,
            destCode=m.dest_code,
            destName=m.dest_name,
            status=m.status,
        )


class DriverRouteSave(BaseModel):
    """批量保存线路（整体替换）"""
    routes: List[DriverRouteCreate]
