"""
车辆管理 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class VehicleCreate(BaseModel):
    plateNumber: str
    vehicleType: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    engineNo: Optional[str] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    purchaseDate: Optional[date] = None
    insuranceExpire: Optional[date] = None
    inspectionExpire: Optional[date] = None
    gpsDeviceId: Optional[str] = None
    remark: Optional[str] = None


class VehicleUpdate(BaseModel):
    plateNumber: Optional[str] = None
    vehicleType: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    engineNo: Optional[str] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    purchaseDate: Optional[date] = None
    insuranceExpire: Optional[date] = None
    inspectionExpire: Optional[date] = None
    gpsDeviceId: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class VehicleOut(BaseModel):
    id: int
    plateNumber: str
    vehicleType: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    engineNo: Optional[str] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    purchaseDate: Optional[date] = None
    insuranceExpire: Optional[date] = None
    inspectionExpire: Optional[date] = None
    gpsDeviceId: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "VehicleOut":
        return cls(
            id=m.id,
            plateNumber=m.plate_number,
            vehicleType=m.vehicle_type,
            brand=m.brand,
            model=m.model,
            color=m.color,
            vin=m.vin,
            engineNo=m.engine_no,
            loadCapacity=float(m.load_capacity) if m.load_capacity is not None else None,
            volumeCapacity=float(m.volume_capacity) if m.volume_capacity is not None else None,
            purchaseDate=m.purchase_date,
            insuranceExpire=m.insurance_expire,
            inspectionExpire=m.inspection_expire,
            gpsDeviceId=m.gps_device_id,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
