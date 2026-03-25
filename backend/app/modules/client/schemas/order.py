from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class OrderCreate(BaseModel):
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    vehicleId: Optional[int] = None
    plateNumber: Optional[str] = None
    driverId: Optional[int] = None
    driverName: Optional[str] = None
    routeId: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    cargoName: Optional[str] = None
    cargoWeight: Optional[float] = None
    cargoVolume: Optional[float] = None
    freightAmount: Optional[float] = None
    planDepartTime: Optional[datetime] = None
    planArriveTime: Optional[datetime] = None
    remark: Optional[str] = None


class OrderUpdate(BaseModel):
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    vehicleId: Optional[int] = None
    plateNumber: Optional[str] = None
    driverId: Optional[int] = None
    driverName: Optional[str] = None
    routeId: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    cargoName: Optional[str] = None
    cargoWeight: Optional[float] = None
    cargoVolume: Optional[float] = None
    freightAmount: Optional[float] = None
    planDepartTime: Optional[datetime] = None
    planArriveTime: Optional[datetime] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: int
    actualDepartTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None


class OrderOut(BaseModel):
    id: int
    orderNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    vehicleId: Optional[int] = None
    plateNumber: Optional[str] = None
    driverId: Optional[int] = None
    driverName: Optional[str] = None
    routeId: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    cargoName: Optional[str] = None
    cargoWeight: Optional[float] = None
    cargoVolume: Optional[float] = None
    freightAmount: Optional[float] = None
    planDepartTime: Optional[datetime] = None
    actualDepartTime: Optional[datetime] = None
    planArriveTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "OrderOut":
        return cls(
            id=m.id,
            orderNo=m.order_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            vehicleId=m.vehicle_id,
            plateNumber=m.plate_number,
            driverId=m.driver_id,
            driverName=m.driver_name,
            routeId=m.route_id,
            origin=m.origin,
            destination=m.destination,
            cargoName=m.cargo_name,
            cargoWeight=float(m.cargo_weight) if m.cargo_weight is not None else None,
            cargoVolume=float(m.cargo_volume) if m.cargo_volume is not None else None,
            freightAmount=float(m.freight_amount) if m.freight_amount is not None else None,
            planDepartTime=m.plan_depart_time,
            actualDepartTime=m.actual_depart_time,
            planArriveTime=m.plan_arrive_time,
            actualArriveTime=m.actual_arrive_time,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
