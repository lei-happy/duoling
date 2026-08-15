from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class EnergySupplierCreate(BaseModel):
    supplierCode: Optional[str] = None
    supplierName: str
    supplierType: int = 9
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    remark: Optional[str] = None


class EnergySupplierUpdate(BaseModel):
    supplierName: Optional[str] = None
    supplierType: Optional[int] = None
    status: Optional[int] = None
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    remark: Optional[str] = None


class EnergySupplierOut(BaseModel):
    id: int
    supplierCode: str
    supplierName: str
    supplierType: int
    status: int
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime

    @classmethod
    def from_model(cls, m) -> "EnergySupplierOut":
        return cls(
            id=m.id,
            supplierCode=m.supplier_code,
            supplierName=m.supplier_name,
            supplierType=m.supplier_type,
            status=m.status,
            contactName=m.contact_name,
            contactPhone=m.contact_phone,
            remark=m.remark,
            createdAt=m.created_at,
        )


class EnergyStationCreate(BaseModel):
    supplierId: int
    stationCode: str
    stationName: str
    address: Optional[str] = None
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    remark: Optional[str] = None


class EnergyStationUpdate(BaseModel):
    stationName: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class EnergyStationOut(BaseModel):
    id: int
    supplierId: int
    stationCode: str
    stationName: str
    address: Optional[str] = None
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    status: int
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "EnergyStationOut":
        return cls(
            id=m.id,
            supplierId=m.supplier_id,
            stationCode=m.station_code,
            stationName=m.station_name,
            address=m.address,
            longitude=m.longitude,
            latitude=m.latitude,
            status=m.status,
            remark=m.remark,
        )
