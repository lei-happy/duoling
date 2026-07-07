"""
承运价规则服务（租户库）
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.carrier_rate import CarrierRate
from app.modules.client.models.billing.carrier_rate_change_log import (
    CarrierRateChangeLog,
)
from app.modules.client.schemas.billing.carrier_rate import (
    CarrierRateCreate, CarrierRateOut, CarrierRateUpdate,
)
from app.modules.client.services.billing.carrier_freight_calc_service import (
    CarrierFreightCalcService,
)
from app.modules.client.services.billing.carrier_freight_calc_task_service import (
    CarrierFreightCalcTaskService,
    TASK_RULE_CHANGED,
)
from app.modules.client.services.billing.standardize_service import StandardizeService


# 影响计算的字段（用于判定 update 是否要触发重算 + 版本号自增）
RATE_BILLING_FIELDS = {
    "origin_code", "origin_region_id",
    "destination_code", "destination_region_id",
    "vehicle_brand", "vehicle_model", "brand_id", "series_id", "match_type",
    "billing_mode", "distance_km", "unit_price", "min_amount",
    "is_bidirectional", "priority", "price_type",
    "effective_date", "expiry_date", "status",
}

# update 时允许显式置为 NULL 的可空列（与 CarrierRate ORM 定义一致）
RATE_UPDATE_NULLABLE_FIELDS = frozenset(
    {
        "origin_region_id",
        "destination_region_id",
        "vehicle_brand",
        "vehicle_model",
        "brand_id",
        "series_id",
        "distance_km",
        "min_amount",
    }
)


def _snapshot(rate: CarrierRate) -> dict:
    return {
        "id": rate.id,
        "contract_id": rate.contract_id,
        "carrier_id": rate.carrier_id,
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


def _infer_match_type(rate: CarrierRate) -> str:
    if rate.series_id is not None:
        return "series"
    if rate.brand_id is not None:
        return "brand"
    return "general"


async def _enqueue_for_rule(
    db: AsyncSession,
    rate: CarrierRate,
    *,
    triggered_by_user_id: Optional[int] = None,
) -> int:
    task_ids = await CarrierFreightCalcService.find_affected_tasks_for_rule(db, rate)
    if not task_ids:
        return 0
    return await CarrierFreightCalcTaskService.enqueue_many_tasks(
        db, task_ids,
        task_type=TASK_RULE_CHANGED,
        source_target_type="rule",
        source_target_id=rate.id,
        priority=8,
        triggered_by_user_id=triggered_by_user_id,
    )


class CarrierRateService:

    @staticmethod
    async def _hydrate_rate_row_regions(db: AsyncSession, rate: CarrierRate) -> None:
        """origin/destination_region_id 为空时，用国标码或名称反查并写入（落库）。"""
        if rate.origin_region_id is None:
            oc = (rate.origin_code or "").strip() or None
            on = (rate.origin or "").strip() or None
            if oc or on:
                r = await StandardizeService.resolve_region(
                    db, region_id=None, code=oc, raw_name=on,
                )
                if r.region_id is not None:
                    rate.origin_region_id = r.region_id
        if rate.destination_region_id is None:
            dc = (rate.destination_code or "").strip() or None
            dn = (rate.destination or "").strip() or None
            if dc or dn:
                r = await StandardizeService.resolve_region(
                    db, region_id=None, code=dc, raw_name=dn,
                )
                if r.region_id is not None:
                    rate.destination_region_id = r.region_id

    @staticmethod
    async def list_by_contract(db: AsyncSession, contract_id: int) -> list:
        result = await db.execute(
            select(CarrierRate).where(
                CarrierRate.contract_id == contract_id,
                CarrierRate.is_deleted == 0,
            ).order_by(CarrierRate.id.desc())
        )
        items = result.scalars().all()
        return [CarrierRateOut.from_model(item).model_dump() for item in items]

    @staticmethod
    async def get_rate(db: AsyncSession, rate_id: int) -> CarrierRate:
        r = await db.execute(
            select(CarrierRate).where(
                CarrierRate.id == rate_id, CarrierRate.is_deleted == 0,
            )
        )
        rate = r.scalar_one_or_none()
        if not rate:
            raise BizException("承运价不存在")
        return rate

    @staticmethod
    async def create_rate(
        db: AsyncSession, data: CarrierRateCreate,
        *, current_user_id: Optional[int] = None,
    ) -> CarrierRate:
        rate = CarrierRate(
            contract_id=data.contractId,
            carrier_id=data.carrierId,
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
        await CarrierRateService._hydrate_rate_row_regions(db, rate)
        rate.match_type = _infer_match_type(rate)
        db.add(rate)
        await db.flush()
        await db.refresh(rate)

        db.add(CarrierRateChangeLog(
            rate_id=rate.id,
            contract_id=rate.contract_id,
            rule_version_before=None,
            rule_version_after=rate.rule_version,
            change_type="create",
            snapshot_before=None,
            snapshot_after=_snapshot(rate),
            operator_id=current_user_id,
        ))

        if rate.status == 1:
            try:
                affected = await _enqueue_for_rule(
                    db, rate, triggered_by_user_id=current_user_id,
                )
                await db.flush()
                last_log = await db.execute(
                    select(CarrierRateChangeLog).where(
                        CarrierRateChangeLog.rate_id == rate.id,
                    ).order_by(CarrierRateChangeLog.id.desc()).limit(1)
                )
                lg = last_log.scalar_one_or_none()
                if lg:
                    lg.affected_task_count = affected
            except Exception:
                pass

        return rate

    @staticmethod
    async def update_rate(
        db: AsyncSession, rate_id: int, data: CarrierRateUpdate,
        *, current_user_id: Optional[int] = None,
    ) -> CarrierRate:
        rate = await CarrierRateService.get_rate(db, rate_id)
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
        update_payload = data.model_dump(exclude_unset=True, mode="python")
        for schema_field, model_field in field_map.items():
            if schema_field not in update_payload:
                continue
            val = update_payload[schema_field]
            if val is None and model_field not in RATE_UPDATE_NULLABLE_FIELDS:
                continue
            if model_field in RATE_BILLING_FIELDS:
                if getattr(rate, model_field) != val:
                    billing_changed = True
            setattr(rate, model_field, val)

        o0, d0 = rate.origin_region_id, rate.destination_region_id
        await CarrierRateService._hydrate_rate_row_regions(db, rate)
        if rate.origin_region_id != o0 or rate.destination_region_id != d0:
            billing_changed = True

        rate.match_type = _infer_match_type(rate)

        if billing_changed:
            rate.rule_version = (rate.rule_version or 1) + 1

        await db.flush()
        await db.refresh(rate)

        db.add(CarrierRateChangeLog(
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
                    select(CarrierRateChangeLog).where(
                        CarrierRateChangeLog.rate_id == rate.id,
                    ).order_by(CarrierRateChangeLog.id.desc()).limit(1)
                )
                lg = last_log.scalar_one_or_none()
                if lg:
                    lg.affected_task_count = affected
            except Exception:
                pass

        return rate

    @staticmethod
    async def delete_rate(
        db: AsyncSession, rate_id: int,
        *, current_user_id: Optional[int] = None,
    ) -> None:
        rate = await CarrierRateService.get_rate(db, rate_id)
        before = _snapshot(rate)
        rate.is_deleted = 1
        rate.rule_version = (rate.rule_version or 1) + 1
        await db.flush()

        db.add(CarrierRateChangeLog(
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
            await _enqueue_for_rule(db, rate, triggered_by_user_id=current_user_id)
        except Exception:
            pass

    @staticmethod
    async def list_change_logs(db: AsyncSession, rate_id: int) -> list[dict]:
        r = await db.execute(
            select(CarrierRateChangeLog).where(
                CarrierRateChangeLog.rate_id == rate_id,
                CarrierRateChangeLog.is_deleted == 0,
            ).order_by(CarrierRateChangeLog.id.desc())
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
                "affectedTaskCount": lg.affected_task_count,
                "remark": lg.remark,
                "createdAt": lg.created_at,
            })
        return out
