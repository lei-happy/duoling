"""
成本规则冲突检测服务

保存/编辑规则前预校验：同一政策范围下，同 fee_type + 同线路 + 同车型 + 生效期重叠
且同价格类型的规则会在匹配时产生同分冲突，这里提前提示。
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.cost_rule import CostRule


def _date_overlap(
    a_start: Optional[date], a_end: Optional[date],
    b_start: Optional[date], b_end: Optional[date],
) -> bool:
    a_start = a_start or date.min
    a_end = a_end or date.max
    b_start = b_start or date.min
    b_end = b_end or date.max
    return a_start <= b_end and b_start <= a_end


class CostRuleConflictService:

    @staticmethod
    async def check_conflict(
        db: AsyncSession,
        *,
        rule_id: Optional[int],
        policy_id: int,
        fee_type: str,
        origin_region_id: Optional[int],
        destination_region_id: Optional[int],
        brand_id: Optional[int],
        series_id: Optional[int],
        price_type: int = 0,
        effective_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
    ) -> dict:
        r = await db.execute(
            select(CostRule).where(
                CostRule.policy_id == policy_id,
                CostRule.fee_type == fee_type,
                CostRule.status == 1,
                CostRule.is_deleted == 0,
            )
        )
        conflicts = []
        for other in r.scalars().all():
            if rule_id and other.id == rule_id:
                continue
            if other.origin_region_id != origin_region_id:
                continue
            if other.destination_region_id != destination_region_id:
                continue
            if other.brand_id != brand_id or other.series_id != series_id:
                continue
            if not _date_overlap(
                effective_date, expiry_date,
                other.effective_date, other.expiry_date,
            ):
                continue
            severity = "error" if other.price_type == price_type else "warning"
            conflicts.append({
                "ruleId": other.id,
                "policyId": other.policy_id,
                "feeType": other.fee_type,
                "pricingMethod": other.pricing_method,
                "unitPrice": float(other.unit_price) if other.unit_price is not None else None,
                "priceType": other.price_type,
                "priority": other.priority,
                "ruleVersion": other.rule_version,
                "effectiveDate": other.effective_date.isoformat() if other.effective_date else None,
                "expiryDate": other.expiry_date.isoformat() if other.expiry_date else None,
                "severity": severity,
            })
        return {
            "conflicts": conflicts,
            "hasError": any(c["severity"] == "error" for c in conflicts),
            "count": len(conflicts),
        }
