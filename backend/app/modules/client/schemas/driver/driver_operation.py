"""
驾驶员运营属性 Schemas
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class DriverOperationOut(BaseModel):
    """运营属性响应"""
    id: int
    driverId: int
    departmentId: Optional[int] = None
    departmentName: Optional[str] = None
    driverType: Optional[int] = None
    residentAreas: Optional[Any] = None
    commonRoutes: Optional[str] = None
    operationStatus: Optional[int] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, dept_name=None) -> "DriverOperationOut":
        return cls(
            id=m.id,
            driverId=m.driver_id,
            departmentId=m.department_id,
            departmentName=dept_name,
            driverType=m.driver_type,
            residentAreas=m.resident_areas,
            commonRoutes=m.common_routes,
            operationStatus=m.operation_status,
            createdAt=m.created_at,
        )
