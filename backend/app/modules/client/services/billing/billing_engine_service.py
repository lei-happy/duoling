"""
计费引擎服务（租户库）
"""

from typing import Optional
from datetime import date
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.freight_contract import FreightContract
from app.modules.client.models.billing.freight_rate import FreightRate


class FreightResult(BaseModel):
    unitPrice: Decimal
    billingMode: int = 0
    distanceKm: Optional[Decimal] = None
    totalAmount: Decimal
    contractId: int
    contractNo: str
    rateId: int
    matchLevel: str
    priceType: int = 0


class BillingEngineService:

    @staticmethod
    def _calc_total(r, quantity: int) -> Decimal:
        if r.billing_mode == 1:
            km = r.distance_km or Decimal("0")
            return r.unit_price * km * quantity
        elif r.billing_mode == 2:
            return r.unit_price
        else:
            return r.unit_price * quantity

    @staticmethod
    def _pick_by_price_type(
        candidates: list, contract_map: dict, match_level: str,
        quantity: int = 1,
    ) -> Optional[FreightResult]:
        """在同级别候选运价中，优先取明确运价(0)，其次预估运价(1)"""
        candidates.sort(key=lambda r: (r.price_type, -r.id))
        if not candidates:
            return None
        r = candidates[0]
        contract = contract_map[r.contract_id]
        total = BillingEngineService._calc_total(r, quantity)
        return FreightResult(
            unitPrice=r.unit_price,
            billingMode=r.billing_mode,
            distanceKm=r.distance_km,
            totalAmount=total,
            contractId=contract.id,
            contractNo=contract.contract_no,
            rateId=r.id,
            matchLevel=match_level,
            priceType=r.price_type,
        )

    @staticmethod
    async def calculate_freight(
        db: AsyncSession,
        customer_id: int,
        origin_code: str,
        destination_code: str,
        vehicle_brand: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        quantity: int = 1,
        billing_date: Optional[date] = None,
    ) -> Optional[FreightResult]:
        if billing_date is None:
            billing_date = date.today()

        active_contracts = await db.execute(
            select(FreightContract).where(
                FreightContract.customer_id == customer_id,
                FreightContract.status == 1,
                FreightContract.is_deleted == 0,
                FreightContract.effective_date <= billing_date,
                FreightContract.expiry_date >= billing_date,
            )
        )
        contracts = active_contracts.scalars().all()
        if not contracts:
            return None

        contract_ids = [c.id for c in contracts]
        contract_map = {c.id: c for c in contracts}

        base_filter = and_(
            FreightRate.contract_id.in_(contract_ids),
            FreightRate.customer_id == customer_id,
            FreightRate.origin_code == origin_code,
            FreightRate.destination_code == destination_code,
            FreightRate.status == 1,
            FreightRate.is_deleted == 0,
        )

        result = await db.execute(
            select(FreightRate).where(base_filter)
        )
        rates = result.scalars().all()
        if not rates:
            return None

        valid_rates = []
        for r in rates:
            if r.effective_date and r.effective_date > billing_date:
                continue
            if r.expiry_date and r.expiry_date < billing_date:
                continue
            valid_rates.append(r)

        if not valid_rates:
            return None

        pick = BillingEngineService._pick_by_price_type

        # 精确匹配：客户+出发地+目的地+品牌+车型
        if vehicle_brand and vehicle_model:
            exact = [
                r for r in valid_rates
                if r.vehicle_brand == vehicle_brand and r.vehicle_model == vehicle_model
            ]
            hit = pick(exact, contract_map, "exact", quantity)
            if hit:
                return hit

        # 品牌匹配：客户+出发地+目的地+品牌
        if vehicle_brand:
            brand = [
                r for r in valid_rates
                if r.vehicle_brand == vehicle_brand and not r.vehicle_model
            ]
            hit = pick(brand, contract_map, "brand", quantity)
            if hit:
                return hit

        # 通用匹配：客户+出发地+目的地
        general = [
            r for r in valid_rates
            if not r.vehicle_brand and not r.vehicle_model
        ]
        hit = pick(general, contract_map, "general", quantity)
        if hit:
            return hit

        return None
