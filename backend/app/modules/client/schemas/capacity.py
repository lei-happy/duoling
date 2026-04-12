"""
运力管理 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CapacityBind(BaseModel):
    """上车（绑定司机+车辆）"""
    driverId: int
    vehicleId: int
    remark: Optional[str] = None


class CapacityUnbind(BaseModel):
    """下车（解绑）"""
    remark: Optional[str] = None


class CapacityOut(BaseModel):
    """运力响应"""
    id: int
    driverId: int
    driverName: str
    driverPhone: str
    vehicleId: int
    plateNumber: str
    status: int
    boundAt: Optional[datetime] = None
    unboundAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, cap) -> "CapacityOut":
        return cls(
            id=cap.id,
            driverId=cap.driver_id,
            driverName=cap.driver_name,
            driverPhone=cap.driver_phone,
            vehicleId=cap.vehicle_id,
            plateNumber=cap.plate_number,
            status=cap.status,
            boundAt=cap.bound_at,
            unboundAt=cap.unbound_at,
            remark=cap.remark,
            createdAt=cap.created_at,
        )


class CapacityLogOut(BaseModel):
    """运力变动记录响应"""
    id: int
    capacityId: int
    driverId: int
    driverName: str
    vehicleId: int
    plateNumber: str
    action: int
    actionTime: Optional[datetime] = None
    operatorId: Optional[int] = None
    operatorName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, log) -> "CapacityLogOut":
        return cls(
            id=log.id,
            capacityId=log.capacity_id,
            driverId=log.driver_id,
            driverName=log.driver_name,
            vehicleId=log.vehicle_id,
            plateNumber=log.plate_number,
            action=log.action,
            actionTime=log.action_time,
            operatorId=log.operator_id,
            operatorName=log.operator_name,
            remark=log.remark,
            createdAt=log.created_at,
        )
