"""
运价费率 Schemas
"""

from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class FreightRateCreate(BaseModel):
    contractId: Optional[int] = None
    customerId: Optional[int] = None
    origin: str
    originCode: str
    destination: str
    destinationCode: str
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    billingMode: int = 0
    distanceKm: Optional[Decimal] = None
    unitPrice: Decimal
    priceType: int = 0
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None


class FreightRateUpdate(BaseModel):
    origin: Optional[str] = None
    originCode: Optional[str] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    billingMode: Optional[int] = None
    distanceKm: Optional[Decimal] = None
    unitPrice: Optional[Decimal] = None
    priceType: Optional[int] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[int] = None


class FreightRateOut(BaseModel):
    id: int
    contractId: int
    customerId: int
    origin: str
    originCode: str
    destination: str
    destinationCode: str
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    billingMode: int
    distanceKm: Optional[float] = None
    unitPrice: float
    priceType: int
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: int
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "FreightRateOut":
        return cls(
            id=m.id,
            contractId=m.contract_id,
            customerId=m.customer_id,
            origin=m.origin,
            originCode=m.origin_code,
            destination=m.destination,
            destinationCode=m.destination_code,
            vehicleBrand=m.vehicle_brand,
            vehicleModel=m.vehicle_model,
            billingMode=m.billing_mode,
            distanceKm=float(m.distance_km) if m.distance_km is not None else None,
            unitPrice=float(m.unit_price),
            priceType=m.price_type,
            effectiveDate=m.effective_date,
            expiryDate=m.expiry_date,
            status=m.status,
            createdAt=m.created_at,
        )
