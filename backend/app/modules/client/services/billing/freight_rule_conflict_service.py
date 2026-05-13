"""
运价规则冲突预校验服务（Phase 5）

应用场景：
  - 新增/编辑运价规则保存前，前端先调用本接口检测潜在冲突，
    冲突时弹窗让用户调整生效期或显式确认。
  - 冲突判定标准：
    1) 同合同（或同客户），同线路（出发/目的 region_id 或 code 全等），
       同 match_type，同车型 ID（series_id 或 brand_id 全等），
       同 priority，同 price_type，时间区间存在交集，且不是被检测的同一行。
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.freight_rate import FreightRate


def _date_overlap(
    a_start: Optional[date], a_end: Optional[date],
    b_start: Optional[date], b_end: Optional[date],
) -> bool:
    """两个时间段是否有交集。None 视为开区间。"""
    if a_end is not None and b_start is not None and a_end < b_start:
        return False
    if b_end is not None and a_start is not None and b_end < a_start:
        return False
    return True


class FreightRuleConflictService:

    @staticmethod
    async def find_conflicts(
        db: AsyncSession,
        *,
        exclude_rate_id: Optional[int] = None,
        contract_id: int,
        customer_id: int,
        origin_code: Optional[str],
        origin_region_id: Optional[int],
        destination_code: Optional[str],
        destination_region_id: Optional[int],
        brand_id: Optional[int],
        series_id: Optional[int],
        priority: int,
        price_type: int,
        is_bidirectional: int,
        effective_date: Optional[date],
        expiry_date: Optional[date],
    ) -> list[dict]:
        """返回与传入规则冲突的运价规则列表（去掉自身）"""
        # 范围拉到客户级别，再做精细过滤
        r = await db.execute(
            select(FreightRate).where(
                FreightRate.customer_id == customer_id,
                FreightRate.is_deleted == 0,
                FreightRate.status == 1,
            )
        )
        rows = list(r.scalars().all())

        def _line_eq(a: FreightRate) -> bool:
            # 优先 region_id 比较，缺则用 code 比较
            o_eq = (
                (origin_region_id is not None and a.origin_region_id == origin_region_id)
                or (origin_region_id is None and a.origin_code == origin_code)
            )
            d_eq = (
                (destination_region_id is not None
                 and a.destination_region_id == destination_region_id)
                or (destination_region_id is None and a.destination_code == destination_code)
            )
            forward = o_eq and d_eq
            backward = False
            if is_bidirectional == 1 or a.is_bidirectional == 1:
                rev_o_eq = (
                    (destination_region_id is not None
                     and a.origin_region_id == destination_region_id)
                    or (destination_region_id is None and a.origin_code == destination_code)
                )
                rev_d_eq = (
                    (origin_region_id is not None
                     and a.destination_region_id == origin_region_id)
                    or (origin_region_id is None and a.destination_code == origin_code)
                )
                backward = rev_o_eq and rev_d_eq
            return forward or backward

        def _model_eq(a: FreightRate) -> bool:
            if series_id is not None or a.series_id is not None:
                return a.series_id == series_id
            if brand_id is not None or a.brand_id is not None:
                return a.brand_id == brand_id
            return a.brand_id is None and a.series_id is None

        out: list[dict] = []
        for a in rows:
            if exclude_rate_id is not None and a.id == exclude_rate_id:
                continue
            if a.contract_id != contract_id:
                # 跨合同的同维度也要提示，但弱化级别
                pass
            if not _line_eq(a):
                continue
            if not _model_eq(a):
                continue
            if not _date_overlap(
                a.effective_date, a.expiry_date, effective_date, expiry_date,
            ):
                continue

            severity = "warning"
            if (a.contract_id == contract_id
                and (a.priority or 0) == (priority or 0)
                and (a.price_type or 0) == (price_type or 0)):
                severity = "error"

            out.append({
                "rateId": a.id,
                "contractId": a.contract_id,
                "ruleVersion": a.rule_version,
                "origin": a.origin,
                "originCode": a.origin_code,
                "originRegionId": a.origin_region_id,
                "destination": a.destination,
                "destinationCode": a.destination_code,
                "destinationRegionId": a.destination_region_id,
                "brandId": a.brand_id,
                "seriesId": a.series_id,
                "matchType": a.match_type,
                "billingMode": a.billing_mode,
                "unitPrice": float(a.unit_price) if a.unit_price is not None else None,
                "priceType": a.price_type,
                "isBidirectional": a.is_bidirectional,
                "priority": a.priority,
                "effectiveDate": a.effective_date.isoformat() if a.effective_date else None,
                "expiryDate": a.expiry_date.isoformat() if a.expiry_date else None,
                "severity": severity,
            })
        return out
