from __future__ import annotations

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
    stationCount: int = 0

    @classmethod
    def from_model(cls, m, *, station_count: int = 0) -> "EnergySupplierOut":
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
            stationCount=station_count,
        )


class EnergyStationProductIn(BaseModel):
    energyType: str
    productId: Optional[int] = None
    productName: Optional[str] = None
    settlementPrice: Decimal
    unit: Optional[str] = None


class EnergyStationProductOut(BaseModel):
    id: int
    energyType: str
    productId: Optional[int] = None
    productName: Optional[str] = None
    settlementPrice: Decimal
    unit: str


class EnergyStationCreate(BaseModel):
    supplierId: int
    stationCode: str
    stationName: str
    address: Optional[str] = None
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    remark: Optional[str] = None
    products: Optional[list[EnergyStationProductIn]] = None


class EnergyStationUpdate(BaseModel):
    stationName: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    status: Optional[int] = None
    remark: Optional[str] = None
    products: Optional[list[EnergyStationProductIn]] = None


class EnergyStationOut(BaseModel):
    id: int
    supplierId: int
    supplierName: Optional[str] = None
    stationCode: str
    stationName: str
    address: Optional[str] = None
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    status: int
    remark: Optional[str] = None
    products: list[EnergyStationProductOut] = []

    @classmethod
    def from_model(
        cls,
        m,
        *,
        supplier_name: Optional[str] = None,
        products: Optional[list[EnergyStationProductOut]] = None,
    ) -> "EnergyStationOut":
        return cls(
            id=m.id,
            supplierId=m.supplier_id,
            supplierName=supplier_name,
            stationCode=m.station_code,
            stationName=m.station_name,
            address=m.address,
            longitude=m.longitude,
            latitude=m.latitude,
            status=m.status,
            remark=m.remark,
            products=products or [],
        )
