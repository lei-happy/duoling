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


class CapacityStatusUpdate(BaseModel):
    """运力运营状态变更"""
    operationStatus: int


class CapacityOut(BaseModel):
    """运力响应"""
    id: int
    driverId: int
    driverName: str
    driverPhone: str
    vehicleId: int
    plateNumber: str
    plateCategory: Optional[str] = None
    trailerPlateNumber: Optional[str] = None
    trailerPlateCategory: Optional[str] = None
    status: int
    boundAt: Optional[datetime] = None
    unboundAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None
    driverAvatar: Optional[str] = None
    departmentName: Optional[str] = None
    operationStatus: Optional[int] = None
    driverOperationStatus: Optional[int] = None
    vehicleType: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        cap,
        plate_category: Optional[str] = None,
        trailer_plate_number: Optional[str] = None,
        trailer_plate_category: Optional[str] = None,
        driver_avatar: Optional[str] = None,
        department_name: Optional[str] = None,
        driver_operation_status: Optional[int] = None,
        vehicle_type: Optional[str] = None,
    ) -> "CapacityOut":
        return cls(
            id=cap.id,
            driverId=cap.driver_id,
            driverName=cap.driver_name,
            driverPhone=cap.driver_phone,
            vehicleId=cap.vehicle_id,
            plateNumber=cap.plate_number,
            plateCategory=plate_category,
            trailerPlateNumber=trailer_plate_number,
            trailerPlateCategory=trailer_plate_category,
            status=cap.status,
            boundAt=cap.bound_at,
            unboundAt=cap.unbound_at,
            remark=cap.remark,
            createdAt=cap.created_at,
            driverAvatar=driver_avatar,
            departmentName=department_name,
            operationStatus=getattr(cap, "operation_status", None),
            driverOperationStatus=driver_operation_status,
            vehicleType=vehicle_type,
        )


class CapacityLogOut(BaseModel):
    """运力变动记录响应"""
    id: int
    capacityId: int
    driverId: int
    driverName: str
    driverCode: Optional[str] = None
    driverPhone: Optional[str] = None
    vehicleId: int
    plateNumber: str
    plateCategory: Optional[str] = None
    action: int
    actionTime: Optional[datetime] = None
    operatorId: Optional[int] = None
    operatorName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        log,
        plate_category: Optional[str] = None,
        driver_code: Optional[str] = None,
        driver_phone: Optional[str] = None,
    ) -> "CapacityLogOut":
        return cls(
            id=log.id,
            capacityId=log.capacity_id,
            driverId=log.driver_id,
            driverName=log.driver_name,
            driverCode=driver_code,
            driverPhone=driver_phone,
            vehicleId=log.vehicle_id,
            plateNumber=log.plate_number,
            plateCategory=plate_category or "YELLOW",
            action=log.action,
            actionTime=log.action_time,
            operatorId=log.operator_id,
            operatorName=log.operator_name,
            remark=log.remark,
            createdAt=log.created_at,
        )
