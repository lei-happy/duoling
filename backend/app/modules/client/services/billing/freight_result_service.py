"""
运费计算结果查询服务（Phase 3）

只做读取，不参与计算。供前端「查看计算明细」抽屉使用。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.freight_calc_result import (
    WaybillFreightResult,
    WaybillFreightResultDetail,
)


def _f(d):
    return float(d) if isinstance(d, Decimal) else d


class FreightResultService:

    @staticmethod
    async def get_active_result_with_detail(
        db: AsyncSession, waybill_id: int
    ) -> Optional[dict]:
        """获取运单当前活跃的 result 主表 + detail 列表"""
        r = await db.execute(
            select(WaybillFreightResult).where(
                WaybillFreightResult.waybill_id == waybill_id,
                WaybillFreightResult.is_active == 1,
                WaybillFreightResult.is_deleted == 0,
            ).order_by(WaybillFreightResult.id.desc()).limit(1)
        )
        result = r.scalar_one_or_none()
        if not result:
            return None

        d = await db.execute(
            select(WaybillFreightResultDetail).where(
                WaybillFreightResultDetail.result_id == result.id,
                WaybillFreightResultDetail.is_deleted == 0,
            ).order_by(WaybillFreightResultDetail.id.asc())
        )
        details = []
        for x in d.scalars().all():
            details.append({
                "id": x.id,
                "waybillCargoId": x.waybill_cargo_id,
                "vehicleBrand": x.vehicle_brand,
                "vehicleModel": x.vehicle_model,
                "brandId": x.brand_id,
                "seriesId": x.series_id,
                "quantity": x.quantity,
                "matchedContractId": x.matched_contract_id,
                "matchedRuleId": x.matched_rule_id,
                "matchedRuleVersion": x.matched_rule_version,
                "originMatchRegionId": x.origin_match_region_id,
                "originMatchLevel": x.origin_match_level,
                "destinationMatchRegionId": x.destination_match_region_id,
                "destinationMatchLevel": x.destination_match_level,
                "direction": x.direction,
                "modelMatchType": x.model_match_type,
                "unitPrice": _f(x.unit_price),
                "billingMode": x.billing_mode,
                "distanceKm": _f(x.distance_km),
                "amount": _f(x.amount),
                "matchScore": x.match_score,
                "matchTraceJson": x.match_trace_json,
                "calcStatus": x.calc_status,
                "errorType": x.error_type,
                "errorMessage": x.error_message,
            })

        return {
            "id": result.id,
            "waybillId": result.waybill_id,
            "waybillVersion": result.waybill_version,
            "isActive": result.is_active,
            "totalAmount": _f(result.total_amount),
            "calcStatus": result.calc_status,
            "calcEngineVersion": result.calc_engine_version,
            "calcTime": result.calc_time,
            "errorMessage": result.error_message,
            "triggeredBy": result.triggered_by,
            "triggeredUserId": result.triggered_user_id,
            "details": details,
        }
