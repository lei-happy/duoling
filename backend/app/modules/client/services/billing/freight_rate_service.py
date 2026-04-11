"""
运价费率服务（租户库）
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.freight_rate import FreightRate
from app.modules.client.schemas.billing.freight_rate import (
    FreightRateCreate, FreightRateUpdate, FreightRateOut,
)


class FreightRateService:

    @staticmethod
    async def list_by_contract(db: AsyncSession, contract_id: int) -> list:
        result = await db.execute(
            select(FreightRate).where(
                FreightRate.contract_id == contract_id,
                FreightRate.is_deleted == 0,
            ).order_by(FreightRate.id.desc())
        )
        items = result.scalars().all()
        return [FreightRateOut.from_model(item).model_dump() for item in items]

    @staticmethod
    async def create_rate(
        db: AsyncSession, data: FreightRateCreate
    ) -> FreightRate:
        rate = FreightRate(
            contract_id=data.contractId,
            customer_id=data.customerId,
            origin=data.origin,
            origin_code=data.originCode,
            destination=data.destination,
            destination_code=data.destinationCode,
            vehicle_brand=data.vehicleBrand,
            vehicle_model=data.vehicleModel,
            billing_mode=data.billingMode,
            distance_km=data.distanceKm,
            unit_price=data.unitPrice,
            price_type=data.priceType,
            effective_date=data.effectiveDate,
            expiry_date=data.expiryDate,
        )
        db.add(rate)
        await db.flush()
        await db.refresh(rate)
        return rate

    @staticmethod
    async def update_rate(
        db: AsyncSession, rate_id: int, data: FreightRateUpdate
    ) -> FreightRate:
        result = await db.execute(
            select(FreightRate).where(
                FreightRate.id == rate_id,
                FreightRate.is_deleted == 0,
            )
        )
        rate = result.scalar_one_or_none()
        if not rate:
            raise BizException("运价不存在")

        field_map = {
            "origin": "origin",
            "originCode": "origin_code",
            "destination": "destination",
            "destinationCode": "destination_code",
            "vehicleBrand": "vehicle_brand",
            "vehicleModel": "vehicle_model",
            "billingMode": "billing_mode",
            "distanceKm": "distance_km",
            "unitPrice": "unit_price",
            "priceType": "price_type",
            "effectiveDate": "effective_date",
            "expiryDate": "expiry_date",
            "status": "status",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(rate, model_field, val)

        await db.flush()
        await db.refresh(rate)
        return rate

    @staticmethod
    async def delete_rate(db: AsyncSession, rate_id: int) -> None:
        result = await db.execute(
            select(FreightRate).where(
                FreightRate.id == rate_id,
                FreightRate.is_deleted == 0,
            )
        )
        rate = result.scalar_one_or_none()
        if not rate:
            raise BizException("运价不存在")
        rate.is_deleted = 1
        await db.flush()
