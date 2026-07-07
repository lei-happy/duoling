"""
承运价规则 Schemas
"""

from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class CarrierRateCreate(BaseModel):
    contractId: Optional[int] = None
    carrierId: Optional[int] = None
    origin: str
    originCode: str
    originRegionId: Optional[int] = None
    destination: str
    destinationCode: str
    destinationRegionId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    billingMode: int = 0
    distanceKm: Optional[Decimal] = None
    unitPrice: Decimal
    minAmount: Optional[Decimal] = None
    priceType: int = 0
    isBidirectional: Optional[int] = 0
    priority: Optional[int] = 0
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None


class CarrierRateUpdate(BaseModel):
    origin: Optional[str] = None
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    billingMode: Optional[int] = None
    distanceKm: Optional[Decimal] = None
    unitPrice: Optional[Decimal] = None
    minAmount: Optional[Decimal] = None
    priceType: Optional[int] = None
    isBidirectional: Optional[int] = None
    priority: Optional[int] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[int] = None


class CarrierRateOut(BaseModel):
    id: int
    contractId: int
    carrierId: int
    origin: str
    originCode: str
    originRegionId: Optional[int] = None
    destination: str
    destinationCode: str
    destinationRegionId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    matchType: Optional[str] = None
    billingMode: int
    distanceKm: Optional[float] = None
    unitPrice: float
    minAmount: Optional[float] = None
    priceType: int
    isBidirectional: Optional[int] = None
    priority: Optional[int] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: int
    ruleVersion: Optional[int] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "CarrierRateOut":
        return cls(
            id=m.id,
            contractId=m.contract_id,
            carrierId=m.carrier_id,
            origin=m.origin,
            originCode=m.origin_code,
            originRegionId=getattr(m, "origin_region_id", None),
            destination=m.destination,
            destinationCode=m.destination_code,
            destinationRegionId=getattr(m, "destination_region_id", None),
            vehicleBrand=m.vehicle_brand,
            vehicleModel=m.vehicle_model,
            brandId=getattr(m, "brand_id", None),
            seriesId=getattr(m, "series_id", None),
            matchType=getattr(m, "match_type", None),
            billingMode=m.billing_mode,
            distanceKm=float(m.distance_km) if m.distance_km is not None else None,
            unitPrice=float(m.unit_price),
            minAmount=float(m.min_amount) if getattr(m, "min_amount", None) is not None else None,
            priceType=m.price_type,
            isBidirectional=getattr(m, "is_bidirectional", None),
            priority=getattr(m, "priority", None),
            effectiveDate=m.effective_date,
            expiryDate=m.expiry_date,
            status=m.status,
            ruleVersion=getattr(m, "rule_version", None),
            createdAt=m.created_at,
        )
