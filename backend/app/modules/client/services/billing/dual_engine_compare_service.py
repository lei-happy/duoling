"""
双引擎回归对比服务（Phase 8）

目的：在切换到新计费引擎前，针对历史已计算的运单进行金额回归核对。
做法：
  - 把历史运单的 freight_amount 视为「旧引擎结果」（旧 BillingEngineService 已被
    重构为 FreightCalcService 门面，但历史金额仍存于 biz_waybill.freight_amount）。
  - 用 FreightCalcService.preview_for_waybill 跑一次 dry_run 试算
    （新算法 + 综合评分 + 反向匹配 + 整单价分摊），得到「新引擎结果」。
  - 输出 diff 报表：
      * status: identical / minor_diff / major_diff / new_unmatched / old_missing
      * minor_diff 阈值：默认 1 元（可配置）
      * 同时返回各运单的 match_trace 摘要，方便人工核对

也可以选择把对比结果写入 biz_waybill_freight_result（is_active=0）作为审计快照，
但当前阶段仅返回内存报表，不污染主数据。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.services.billing.freight_calc_service import (
    FreightCalcService,
)


@dataclass
class WaybillDiffItem:
    waybill_id: int
    waybill_no: str
    customer_id: Optional[int]
    customer_name: Optional[str]
    origin: Optional[str]
    destination: Optional[str]
    old_amount: Optional[Decimal]
    new_amount: Optional[Decimal]
    diff: Optional[Decimal]
    diff_pct: Optional[float]
    status: str  # identical / minor_diff / major_diff / new_unmatched / old_missing
    new_calc_status: str
    new_error: Optional[str] = None
    new_error_type: Optional[str] = None
    cargo_count: int = 0


@dataclass
class DualEngineCompareReport:
    total: int = 0
    identical: int = 0
    minor_diff: int = 0
    major_diff: int = 0
    new_unmatched: int = 0
    old_missing: int = 0
    items: list[WaybillDiffItem] = field(default_factory=list)


class DualEngineCompareService:

    @staticmethod
    async def _load_cargoes(
        db: AsyncSession, waybill_id: int
    ) -> list[WaybillCargo]:
        r = await db.execute(
            select(WaybillCargo).where(
                WaybillCargo.waybill_id == waybill_id,
                WaybillCargo.is_deleted == 0,
            ).order_by(WaybillCargo.sort_order.asc(), WaybillCargo.id.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def compare_waybill(
        db: AsyncSession, waybill: Waybill,
        billing_date: Optional[date] = None,
        minor_threshold: Decimal = Decimal("1"),
    ) -> WaybillDiffItem:
        cargoes = await DualEngineCompareService._load_cargoes(db, waybill.id)
        summary = await FreightCalcService.preview_for_waybill(
            db, waybill, cargoes, billing_date,
        )

        old_amt = (
            Decimal(str(waybill.freight_amount))
            if waybill.freight_amount is not None else None
        )
        new_amt = summary.total_amount or Decimal("0")
        diff: Optional[Decimal] = None
        diff_pct: Optional[float] = None

        # 聚合 cargo 级错误，便于运营核对
        err_types: list[str] = []
        err_messages: list[str] = []
        for cr in summary.cargo_results:
            if cr.error_type and cr.error_type not in err_types:
                err_types.append(cr.error_type)
            if cr.error_message and cr.error_message not in err_messages:
                err_messages.append(cr.error_message)
        new_error_type = ",".join(err_types) if err_types else None
        new_error = (
            "; ".join(err_messages) if err_messages else summary.error_message
        )

        if old_amt is None:
            status = "old_missing"
        elif summary.calc_status in ("exception", "failed"):
            status = "new_unmatched"
            diff = (new_amt or Decimal("0")) - (old_amt or Decimal("0"))
        else:
            diff = (new_amt or Decimal("0")) - (old_amt or Decimal("0"))
            abs_diff = abs(diff)
            if abs_diff <= Decimal("0.01"):
                status = "identical"
            elif abs_diff <= minor_threshold:
                status = "minor_diff"
            else:
                status = "major_diff"
            if old_amt and old_amt != 0:
                diff_pct = float(diff) / float(old_amt)

        return WaybillDiffItem(
            waybill_id=waybill.id,
            waybill_no=waybill.waybill_no,
            customer_id=waybill.customer_id,
            customer_name=waybill.customer_name,
            origin=waybill.origin,
            destination=waybill.destination,
            old_amount=old_amt,
            new_amount=new_amt,
            diff=diff,
            diff_pct=diff_pct,
            status=status,
            new_calc_status=summary.calc_status,
            new_error=new_error,
            new_error_type=new_error_type,
            cargo_count=len(cargoes),
        )

    @staticmethod
    async def compare_batch(
        db: AsyncSession,
        *,
        customer_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        only_calculated: bool = True,
        limit: int = 200,
        minor_threshold: Decimal = Decimal("1"),
    ) -> DualEngineCompareReport:
        """对一段历史运单进行双引擎对比。"""
        q = select(Waybill).where(Waybill.is_deleted == 0)
        if customer_id:
            q = q.where(Waybill.customer_id == customer_id)
        if date_from:
            q = q.where(Waybill.created_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            q = q.where(Waybill.created_at < datetime.combine(date_to, datetime.max.time()))
        if only_calculated:
            q = q.where(Waybill.freight_amount.is_not(None))
        q = q.order_by(Waybill.id.desc()).limit(limit)

        r = await db.execute(q)
        waybills = list(r.scalars().all())

        report = DualEngineCompareReport(total=len(waybills))
        for wb in waybills:
            try:
                item = await DualEngineCompareService.compare_waybill(
                    db, wb, billing_date=None,
                    minor_threshold=minor_threshold,
                )
            except Exception as e:  # noqa
                item = WaybillDiffItem(
                    waybill_id=wb.id,
                    waybill_no=wb.waybill_no,
                    customer_id=wb.customer_id,
                    customer_name=wb.customer_name,
                    origin=wb.origin,
                    destination=wb.destination,
                    old_amount=(Decimal(str(wb.freight_amount))
                                if wb.freight_amount is not None else None),
                    new_amount=None,
                    diff=None,
                    diff_pct=None,
                    status="new_unmatched",
                    new_calc_status="error",
                    new_error=str(e)[:255],
                    cargo_count=0,
                )

            report.items.append(item)
            if item.status == "identical":
                report.identical += 1
            elif item.status == "minor_diff":
                report.minor_diff += 1
            elif item.status == "major_diff":
                report.major_diff += 1
            elif item.status == "new_unmatched":
                report.new_unmatched += 1
            elif item.status == "old_missing":
                report.old_missing += 1

        return report

    @staticmethod
    def report_to_dict(report: DualEngineCompareReport) -> dict:
        def _f(d):
            if d is None:
                return None
            if isinstance(d, Decimal):
                return float(d)
            return d

        return {
            "total": report.total,
            "identical": report.identical,
            "minorDiff": report.minor_diff,
            "majorDiff": report.major_diff,
            "newUnmatched": report.new_unmatched,
            "oldMissing": report.old_missing,
            "items": [
                {
                    "waybillId": i.waybill_id,
                    "waybillNo": i.waybill_no,
                    "customerId": i.customer_id,
                    "customerName": i.customer_name,
                    "origin": i.origin,
                    "destination": i.destination,
                    "oldAmount": _f(i.old_amount),
                    "newAmount": _f(i.new_amount),
                    "diff": _f(i.diff),
                    "diffPct": i.diff_pct,
                    "status": i.status,
                    "newCalcStatus": i.new_calc_status,
                    "newErrorType": i.new_error_type,
                    "newError": i.new_error,
                    "cargoCount": i.cargo_count,
                }
                for i in report.items
            ],
        }
