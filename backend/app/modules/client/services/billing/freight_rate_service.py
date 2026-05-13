"""
运价费率服务（租户库）
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.freight_rate import FreightRate
from app.modules.client.models.billing.freight_rate_change_log import FreightRateChangeLog
from app.modules.client.schemas.billing.freight_rate import (
    FreightRateCreate, FreightRateOut, FreightRateUpdate,
)
from app.modules.client.services.billing.freight_calc_service import FreightCalcService
from app.modules.client.services.billing.freight_calc_task_service import (
    FreightCalcTaskService,
    TASK_RULE_CHANGED,
)


# 影响计算的字段（用于判定 update 是否要触发重算 + 版本号自增）
RATE_BILLING_FIELDS = {
    "origin_code", "origin_region_id",
    "destination_code", "destination_region_id",
    "vehicle_brand", "vehicle_model", "brand_id", "series_id", "match_type",
    "billing_mode", "distance_km", "unit_price", "min_amount",
    "is_bidirectional", "priority", "price_type",
    "effective_date", "expiry_date", "status",
}


def _snapshot(rate: FreightRate) -> dict:
    return {
        "id": rate.id,
        "contract_id": rate.contract_id,
        "customer_id": rate.customer_id,
        "origin": rate.origin,
        "origin_code": rate.origin_code,
        "origin_region_id": rate.origin_region_id,
        "destination": rate.destination,
        "destination_code": rate.destination_code,
        "destination_region_id": rate.destination_region_id,
        "vehicle_brand": rate.vehicle_brand,
        "vehicle_model": rate.vehicle_model,
        "brand_id": rate.brand_id,
        "series_id": rate.series_id,
        "match_type": rate.match_type,
        "billing_mode": rate.billing_mode,
        "distance_km": float(rate.distance_km) if rate.distance_km is not None else None,
        "unit_price": float(rate.unit_price) if rate.unit_price is not None else None,
        "min_amount": float(rate.min_amount) if rate.min_amount is not None else None,
        "price_type": rate.price_type,
        "is_bidirectional": rate.is_bidirectional,
        "priority": rate.priority,
        "effective_date": rate.effective_date.isoformat() if rate.effective_date else None,
        "expiry_date": rate.expiry_date.isoformat() if rate.expiry_date else None,
        "status": rate.status,
        "rule_version": rate.rule_version,
    }


def _infer_match_type(rate: FreightRate) -> str:
    if rate.series_id is not None:
        return "series"
    if rate.brand_id is not None:
        return "brand"
    return "general"


async def _enqueue_for_rule(
    db: AsyncSession,
    rate: FreightRate,
    *,
    triggered_by_user_id: Optional[int] = None,
) -> int:
    waybill_ids = await FreightCalcService.find_affected_waybills_for_rule(
        db, rate,
    )
    if not waybill_ids:
        return 0
    return await FreightCalcTaskService.enqueue_many_waybills(
        db, waybill_ids,
        task_type=TASK_RULE_CHANGED,
        source_target_type="rule",
        source_target_id=rate.id,
        priority=8,
        triggered_by_user_id=triggered_by_user_id,
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
    async def get_rate(db: AsyncSession, rate_id: int) -> FreightRate:
        r = await db.execute(
            select(FreightRate).where(
                FreightRate.id == rate_id, FreightRate.is_deleted == 0,
            )
        )
        rate = r.scalar_one_or_none()
        if not rate:
            raise BizException("运价不存在")
        return rate

    @staticmethod
    async def create_rate(
        db: AsyncSession, data: FreightRateCreate,
        *, current_user_id: Optional[int] = None,
    ) -> FreightRate:
        rate = FreightRate(
            contract_id=data.contractId,
            customer_id=data.customerId,
            origin=data.origin,
            origin_code=data.originCode,
            origin_region_id=getattr(data, "originRegionId", None),
            destination=data.destination,
            destination_code=data.destinationCode,
            destination_region_id=getattr(data, "destinationRegionId", None),
            vehicle_brand=data.vehicleBrand,
            vehicle_model=data.vehicleModel,
            brand_id=getattr(data, "brandId", None),
            series_id=getattr(data, "seriesId", None),
            billing_mode=data.billingMode,
            distance_km=data.distanceKm,
            unit_price=data.unitPrice,
            min_amount=getattr(data, "minAmount", None),
            price_type=data.priceType,
            is_bidirectional=int(getattr(data, "isBidirectional", 0) or 0),
            priority=int(getattr(data, "priority", 0) or 0),
            effective_date=data.effectiveDate,
            expiry_date=data.expiryDate,
            rule_version=1,
        )
        rate.match_type = _infer_match_type(rate)
        db.add(rate)
        await db.flush()
        await db.refresh(rate)

        db.add(FreightRateChangeLog(
            rate_id=rate.id,
            contract_id=rate.contract_id,
            rule_version_before=None,
            rule_version_after=rate.rule_version,
            change_type="create",
            snapshot_before=None,
            snapshot_after=_snapshot(rate),
            operator_id=current_user_id,
        ))

        # 新规则启用时立即触发受影响运单重算
        if rate.status == 1:
            try:
                affected = await _enqueue_for_rule(
                    db, rate, triggered_by_user_id=current_user_id,
                )
                # 回填影响数到 change_log（最近一条）
                await db.flush()
                last_log = await db.execute(
                    select(FreightRateChangeLog).where(
                        FreightRateChangeLog.rate_id == rate.id,
                    ).order_by(FreightRateChangeLog.id.desc()).limit(1)
                )
                lg = last_log.scalar_one_or_none()
                if lg:
                    lg.affected_waybill_count = affected
            except Exception:
                pass

        return rate

    @staticmethod
    async def update_rate(
        db: AsyncSession, rate_id: int, data: FreightRateUpdate,
        *, current_user_id: Optional[int] = None,
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

        before = _snapshot(rate)

        field_map = {
            "origin": "origin",
            "originCode": "origin_code",
            "originRegionId": "origin_region_id",
            "destination": "destination",
            "destinationCode": "destination_code",
            "destinationRegionId": "destination_region_id",
            "vehicleBrand": "vehicle_brand",
            "vehicleModel": "vehicle_model",
            "brandId": "brand_id",
            "seriesId": "series_id",
            "billingMode": "billing_mode",
            "distanceKm": "distance_km",
            "unitPrice": "unit_price",
            "minAmount": "min_amount",
            "priceType": "price_type",
            "isBidirectional": "is_bidirectional",
            "priority": "priority",
            "effectiveDate": "effective_date",
            "expiryDate": "expiry_date",
            "status": "status",
        }
        billing_changed = False
        for schema_field, model_field in field_map.items():
            if not hasattr(data, schema_field):
                continue
            val = getattr(data, schema_field, None)
            if val is None:
                continue
            if model_field in RATE_BILLING_FIELDS:
                if getattr(rate, model_field) != val:
                    billing_changed = True
            setattr(rate, model_field, val)

        rate.match_type = _infer_match_type(rate)

        if billing_changed:
            rate.rule_version = (rate.rule_version or 1) + 1

        await db.flush()
        await db.refresh(rate)

        db.add(FreightRateChangeLog(
            rate_id=rate.id,
            contract_id=rate.contract_id,
            rule_version_before=before.get("rule_version"),
            rule_version_after=rate.rule_version,
            change_type="update",
            snapshot_before=before,
            snapshot_after=_snapshot(rate),
            operator_id=current_user_id,
        ))

        if billing_changed:
            try:
                affected = await _enqueue_for_rule(
                    db, rate, triggered_by_user_id=current_user_id,
                )
                last_log = await db.execute(
                    select(FreightRateChangeLog).where(
                        FreightRateChangeLog.rate_id == rate.id,
                    ).order_by(FreightRateChangeLog.id.desc()).limit(1)
                )
                lg = last_log.scalar_one_or_none()
                if lg:
                    lg.affected_waybill_count = affected
            except Exception:
                pass

        return rate

    @staticmethod
    async def delete_rate(
        db: AsyncSession, rate_id: int,
        *, current_user_id: Optional[int] = None,
    ) -> None:
        result = await db.execute(
            select(FreightRate).where(
                FreightRate.id == rate_id,
                FreightRate.is_deleted == 0,
            )
        )
        rate = result.scalar_one_or_none()
        if not rate:
            raise BizException("运价不存在")

        before = _snapshot(rate)
        rate.is_deleted = 1
        rate.rule_version = (rate.rule_version or 1) + 1
        await db.flush()

        db.add(FreightRateChangeLog(
            rate_id=rate.id,
            contract_id=rate.contract_id,
            rule_version_before=before.get("rule_version"),
            rule_version_after=rate.rule_version,
            change_type="delete",
            snapshot_before=before,
            snapshot_after=None,
            operator_id=current_user_id,
        ))

        try:
            await _enqueue_for_rule(
                db, rate, triggered_by_user_id=current_user_id,
            )
        except Exception:
            pass

    @staticmethod
    async def list_change_logs(
        db: AsyncSession, rate_id: int
    ) -> list[dict]:
        r = await db.execute(
            select(FreightRateChangeLog).where(
                FreightRateChangeLog.rate_id == rate_id,
                FreightRateChangeLog.is_deleted == 0,
            ).order_by(FreightRateChangeLog.id.desc())
        )
        out: list[dict] = []
        for lg in r.scalars().all():
            out.append({
                "id": lg.id,
                "rateId": lg.rate_id,
                "contractId": lg.contract_id,
                "ruleVersionBefore": lg.rule_version_before,
                "ruleVersionAfter": lg.rule_version_after,
                "changeType": lg.change_type,
                "snapshotBefore": lg.snapshot_before,
                "snapshotAfter": lg.snapshot_after,
                "operatorId": lg.operator_id,
                "affectedWaybillCount": lg.affected_waybill_count,
                "remark": lg.remark,
                "createdAt": lg.created_at,
            })
        return out
