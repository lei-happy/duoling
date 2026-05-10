"""
车辆管理 Schemas

前端提交时核心字段与扩展字段合并在一个请求体中，
后端 Service 层负责拆分写入 biz_vehicle 和 biz_vehicle_ext 两张表。
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class VehicleCreate(BaseModel):
    """创建车辆（核心+扩展字段合并提交）"""
    plateNumber: str
    trailerId: Optional[int] = None
    # 扩展字段
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
    """更新车辆"""
    plateNumber: Optional[str] = None
    trailerId: Optional[int] = None
    status: Optional[int] = None
    # 扩展字段
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


class VehicleStatusUpdate(BaseModel):
    """车辆状态变更"""
    status: int
    statusSource: str = "manual"


class VehicleOut(BaseModel):
    """车辆响应（核心+扩展合并输出）"""
    id: int
    plateNumber: str
    trailerId: Optional[int] = None
    trailerPlateNumber: Optional[str] = None
    status: int
    statusSource: Optional[str] = None
    # 扩展字段
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
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, vehicle, ext=None, trailer_plate=None) -> "VehicleOut":
        """从核心表+扩展表组装输出"""
        data = dict(
            id=vehicle.id,
            plateNumber=vehicle.plate_number,
            trailerId=vehicle.trailer_id,
            trailerPlateNumber=trailer_plate,
            status=vehicle.status,
            statusSource=vehicle.status_source,
            createdAt=vehicle.created_at,
        )
        if ext:
            data.update(
                vehicleType=ext.vehicle_type,
                brand=ext.brand,
                model=ext.model,
                color=ext.color,
                vin=ext.vin,
                engineNo=ext.engine_no,
                loadCapacity=float(ext.load_capacity) if ext.load_capacity is not None else None,
                volumeCapacity=float(ext.volume_capacity) if ext.volume_capacity is not None else None,
                purchaseDate=ext.purchase_date,
                insuranceExpire=ext.insurance_expire,
                inspectionExpire=ext.inspection_expire,
                gpsDeviceId=ext.gps_device_id,
                remark=ext.remark,
            )
        return cls(**data)
