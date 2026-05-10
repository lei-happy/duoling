"""
挂车管理 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class TrailerCreate(BaseModel):
    """创建挂车（核心+扩展字段合并提交）"""
    plateNumber: str
    # 扩展字段
    trailerType: Optional[str] = None
    axleCount: Optional[int] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    parkingSpots: Optional[int] = None
    purchaseDate: Optional[date] = None
    remark: Optional[str] = None


class TrailerUpdate(BaseModel):
    """更新挂车"""
    plateNumber: Optional[str] = None
    status: Optional[int] = None
    # 扩展字段
    trailerType: Optional[str] = None
    axleCount: Optional[int] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    parkingSpots: Optional[int] = None
    purchaseDate: Optional[date] = None
    remark: Optional[str] = None


class TrailerOut(BaseModel):
    """挂车响应（核心+扩展合并输出）"""
    id: int
    plateNumber: str
    vehiclePlateNumber: Optional[str] = None
    status: int
    # 扩展字段
    trailerType: Optional[str] = None
    axleCount: Optional[int] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    parkingSpots: Optional[int] = None
    purchaseDate: Optional[date] = None
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, trailer, ext=None, vehicle_plate=None) -> "TrailerOut":
        """从核心表+扩展表组装输出"""
        data = dict(
            id=trailer.id,
            plateNumber=trailer.plate_number,
            vehiclePlateNumber=vehicle_plate,
            status=trailer.status,
            createdAt=trailer.created_at,
        )
        if ext:
            data.update(
                trailerType=ext.trailer_type,
                axleCount=ext.axle_count,
                loadCapacity=float(ext.load_capacity) if ext.load_capacity is not None else None,
                volumeCapacity=float(ext.volume_capacity) if ext.volume_capacity is not None else None,
                length=float(ext.length) if ext.length is not None else None,
                width=float(ext.width) if ext.width is not None else None,
                height=float(ext.height) if ext.height is not None else None,
                parkingSpots=ext.parking_spots,
                purchaseDate=ext.purchase_date,
                remark=ext.remark,
            )
        return cls(**data)


class TrailerSimpleOut(BaseModel):
    """挂车简要信息（用于下拉选择）"""
    id: int
    plateNumber: str
