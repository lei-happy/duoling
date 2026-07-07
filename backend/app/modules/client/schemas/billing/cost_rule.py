"""
成本费用规则 Schemas
"""

from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class CostRuleCreate(BaseModel):
    policyId: Optional[int] = None
    feeType: str
    feeName: Optional[str] = None
    direction: int = 1
    pricingMethod: str = "per_vehicle"
    qtyDimension: Optional[str] = None
    multiplyByQty: int = 0
    unitPrice: Decimal = Decimal("0")
    distanceKm: Optional[Decimal] = None
    minAmount: Optional[Decimal] = None
    maxAmount: Optional[Decimal] = None
    roundMode: int = 0
    tiersJson: Optional[list] = None
    percentBase: Optional[str] = None
    ratePercent: Optional[Decimal] = None
    payeeType: int = 1
    originRegionId: Optional[int] = None
    originCode: Optional[str] = None
    origin: Optional[str] = None
    destinationRegionId: Optional[int] = None
    destinationCode: Optional[str] = None
    destination: Optional[str] = None
    isBidirectional: int = 0
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    priceType: int = 0
    priority: int = 0
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    remark: Optional[str] = None


class CostRuleUpdate(BaseModel):
    feeType: Optional[str] = None
    feeName: Optional[str] = None
    direction: Optional[int] = None
    pricingMethod: Optional[str] = None
    qtyDimension: Optional[str] = None
    multiplyByQty: Optional[int] = None
    unitPrice: Optional[Decimal] = None
    distanceKm: Optional[Decimal] = None
    minAmount: Optional[Decimal] = None
    maxAmount: Optional[Decimal] = None
    roundMode: Optional[int] = None
    tiersJson: Optional[list] = None
    percentBase: Optional[str] = None
    ratePercent: Optional[Decimal] = None
    payeeType: Optional[int] = None
    originRegionId: Optional[int] = None
    originCode: Optional[str] = None
    origin: Optional[str] = None
    destinationRegionId: Optional[int] = None
    destinationCode: Optional[str] = None
    destination: Optional[str] = None
    isBidirectional: Optional[int] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    priceType: Optional[int] = None
    priority: Optional[int] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class CostRuleOut(BaseModel):
    id: int
    policyId: int
    feeType: str
    feeName: Optional[str] = None
    direction: int
    pricingMethod: str
    qtyDimension: Optional[str] = None
    multiplyByQty: int
    unitPrice: float
    distanceKm: Optional[float] = None
    minAmount: Optional[float] = None
    maxAmount: Optional[float] = None
    roundMode: int
    tiersJson: Optional[list] = None
    percentBase: Optional[str] = None
    ratePercent: Optional[float] = None
    payeeType: int
    originRegionId: Optional[int] = None
    originCode: Optional[str] = None
    origin: Optional[str] = None
    destinationRegionId: Optional[int] = None
    destinationCode: Optional[str] = None
    destination: Optional[str] = None
    isBidirectional: int
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    priceType: int
    priority: int
    ruleVersion: int
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "CostRuleOut":
        return cls(
            id=m.id,
            policyId=m.policy_id,
            feeType=m.fee_type,
            feeName=m.fee_name,
            direction=m.direction,
            pricingMethod=m.pricing_method,
            qtyDimension=m.qty_dimension,
            multiplyByQty=m.multiply_by_qty,
            unitPrice=float(m.unit_price) if m.unit_price is not None else 0.0,
            distanceKm=float(m.distance_km) if m.distance_km is not None else None,
            minAmount=float(m.min_amount) if m.min_amount is not None else None,
            maxAmount=float(m.max_amount) if m.max_amount is not None else None,
            roundMode=m.round_mode,
            tiersJson=m.tiers_json,
            percentBase=m.percent_base,
            ratePercent=float(m.rate_percent) if m.rate_percent is not None else None,
            payeeType=m.payee_type,
            originRegionId=m.origin_region_id,
            originCode=m.origin_code,
            origin=m.origin,
            destinationRegionId=m.destination_region_id,
            destinationCode=m.destination_code,
            destination=m.destination,
            isBidirectional=m.is_bidirectional,
            brandId=m.brand_id,
            seriesId=m.series_id,
            priceType=m.price_type,
            priority=m.priority,
            ruleVersion=m.rule_version,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
