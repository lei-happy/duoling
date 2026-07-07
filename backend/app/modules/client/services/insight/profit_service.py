"""
经营驾驶舱 - 利润总览（老板视角收入成本 BI）服务

面向老板视角，一屏呈现 收入 / 成本 / 毛利 / 毛利率，并可下钻承运结构、
成本构成、客户毛利。与「运单总览」（收入侧）并列。

设计要点（口径已确认）：
1. 收入：`biz_waybill_freight_result.total_amount`（is_active=1）为准，
   无引擎结果时回退 `biz_waybill.freight_amount`。
2. 成本：`biz_task_cost_result.total_cost_amount`（is_active=1），经
   `biz_task_waybill_item` 按台数分摊回运单：
       运单成本 = Σ_tasks ( tcr.total_cost_amount * twi.quantity / 任务总台数 )
   任务总台数取该任务下 SUM(twi.quantity)，保证任务成本被 100% 分摊。
3. 粒度/归期：运单粒度，统一按 `biz_waybill.created_at` 归期，软删过滤
   `is_deleted = 0`。
4. 毛利 = 收入 - 成本；毛利率 = 毛利 / 收入（收入为 0 时返回 None，前端显示「—」）。
5. 成本覆盖率 = 有成本运单收入 / 总收入，用于提示「未产生成本运单拉高毛利」的偏差。

KPI 卡片口径与「运单总览」对齐：当日累计值 + 近 30 日趋势 + 周同比 + 日同比。
"""

from __future__ import annotations

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, case, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.freight_calc_result import (
    WaybillFreightResult,
)
from app.modules.client.models.billing.task_cost_result import (
    TaskCostResult,
    TaskCostResultItem,
)
from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill


# ---------------------------------------------------------------------------
# 静态字典
# ---------------------------------------------------------------------------

_CARRIER_TYPE_LABELS = {
    1: "自有车",
    2: "承运商",
    3: "社会运力",
}

_UNKNOWN_LABEL = "未知"


def _to_float(value: Any) -> float:
    """Decimal/None/数字 → float（None 视为 0）。"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _safe_growth_rate(current: float, previous: float) -> Optional[float]:
    """环比增长率：previous=0 返回 None（前端显示「—」）。"""
    if previous == 0:
        return None
    return (current - previous) / previous


def _safe_margin(revenue: float, cost: float) -> Optional[float]:
    """毛利率：收入为 0 时返回 None。"""
    if revenue == 0:
        return None
    return (revenue - cost) / revenue


def _coerce_dt(value: Any) -> datetime:
    """date → datetime；datetime 透传。"""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    raise TypeError(f"Unsupported datetime type: {type(value)}")


class ProfitService:
    """利润总览聚合查询服务（收入 - 分摊成本 = 毛利）"""

    # ------------------------------------------------------------------
    # 公共子查询：成本分摊 / 收入引擎结果
    # ------------------------------------------------------------------

    @staticmethod
    def _task_qty_subq():
        """每任务总台数（分摊分母）：task_id -> SUM(twi.quantity)。"""
        return (
            select(
                TaskWaybillItem.task_id.label("task_id"),
                func.sum(TaskWaybillItem.quantity).label("total_qty"),
            )
            .where(TaskWaybillItem.is_deleted == 0)
            .group_by(TaskWaybillItem.task_id)
            .subquery()
        )

    @staticmethod
    def _wb_cost_subq():
        """分摊到运单的成本：waybill_id -> Σ(tcr.total_cost_amount * qty / 任务总台数)。"""
        task_qty = ProfitService._task_qty_subq()
        return (
            select(
                TaskWaybillItem.waybill_id.label("waybill_id"),
                func.coalesce(
                    func.sum(
                        TaskCostResult.total_cost_amount
                        * TaskWaybillItem.quantity
                        / func.nullif(task_qty.c.total_qty, 0)
                    ),
                    0,
                ).label("cost"),
            )
            .select_from(TaskWaybillItem)
            .join(task_qty, task_qty.c.task_id == TaskWaybillItem.task_id)
            .join(
                Task,
                and_(Task.id == TaskWaybillItem.task_id, Task.is_deleted == 0),
            )
            .join(
                TaskCostResult,
                and_(
                    TaskCostResult.task_id == TaskWaybillItem.task_id,
                    TaskCostResult.is_active == 1,
                    TaskCostResult.is_deleted == 0,
                ),
            )
            .where(TaskWaybillItem.is_deleted == 0)
            .group_by(TaskWaybillItem.waybill_id)
            .subquery()
        )

    @staticmethod
    def _wb_rev_subq():
        """运单收入引擎结果：waybill_id -> total_amount（is_active=1）。"""
        return (
            select(
                WaybillFreightResult.waybill_id.label("waybill_id"),
                func.coalesce(
                    func.sum(WaybillFreightResult.total_amount), 0
                ).label("rev"),
            )
            .where(
                WaybillFreightResult.is_active == 1,
                WaybillFreightResult.is_deleted == 0,
            )
            .group_by(WaybillFreightResult.waybill_id)
            .subquery()
        )

    # ------------------------------------------------------------------
    # 1. 核心 KPI（收入 / 成本 / 毛利 / 毛利率）
    # ------------------------------------------------------------------

    @staticmethod
    def _week_monday_start(d: date) -> datetime:
        monday = d - timedelta(days=d.weekday())
        return datetime.combine(monday, datetime.min.time())

    @staticmethod
    async def kpi_summary(
        db: AsyncSession, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        """4 KPI：收入 / 成本 / 毛利 / 毛利率（当日值 + 近 30 日趋势 + 周同比 + 日同比）。

        `start`/`end` 为接口兼容保留，本卡片一律按服务端当前时刻聚合，
        与「运单总览」KPI 口径一致。
        """
        _ = (start, end)

        now = datetime.now()
        today_d = now.date()
        today_start = datetime.combine(today_d, datetime.min.time())
        yesterday_d = today_d - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday_d, datetime.min.time())
        trend_start = datetime.combine(
            today_d - timedelta(days=29), datetime.min.time()
        )

        today_m = await ProfitService._totals(db, today_start, now, inclusive=True)
        yesterday_same_m = await ProfitService._totals(
            db, yesterday_start, now - timedelta(days=1), inclusive=True
        )

        this_monday = ProfitService._week_monday_start(today_d)
        last_monday = this_monday - timedelta(days=7)
        span = now - this_monday
        this_week_m = await ProfitService._totals(
            db, this_monday, now, inclusive=True
        )
        last_week_m = await ProfitService._totals(
            db, last_monday, last_monday + span, inclusive=True
        )

        daily_rows = await ProfitService._daily_rows(db, trend_start, now)
        by_d = {r["date"]: r for r in daily_rows}

        def _trend30d(field: str) -> List[Dict[str, Any]]:
            out: List[Dict[str, Any]] = []
            for i in range(30):
                d = today_d - timedelta(days=29 - i)
                key = str(d)
                row = by_d.get(key)
                if field == "grossMargin":
                    v = _safe_margin(row["revenue"], row["cost"]) if row else None
                    out.append({"date": key, "value": v})
                elif field == "grossProfit":
                    v = (row["revenue"] - row["cost"]) if row else 0.0
                    out.append({"date": key, "value": float(v)})
                else:
                    v = row[field] if row else 0.0
                    out.append({"date": key, "value": float(v)})
            return out

        def _amount_metric(field: str) -> Dict[str, Any]:
            tv = float(today_m[field])
            y = float(yesterday_same_m[field])
            wc = float(this_week_m[field])
            wp = float(last_week_m[field])
            return {
                "todayValue": tv,
                "weekOverWeekRate": _safe_growth_rate(wc, wp),
                "dayOverDayRate": _safe_growth_rate(tv, y),
                "trend30d": _trend30d(field),
            }

        def _margin_metric() -> Dict[str, Any]:
            tv = _safe_margin(today_m["revenue"], today_m["cost"])
            y = _safe_margin(
                yesterday_same_m["revenue"], yesterday_same_m["cost"]
            )
            wc = _safe_margin(this_week_m["revenue"], this_week_m["cost"])
            wp = _safe_margin(last_week_m["revenue"], last_week_m["cost"])
            return {
                # 毛利率本身即比率，todayValue 为当日毛利率（0-1）
                "todayValue": tv,
                # 环比为「百分点差」（当期毛利率 - 上期毛利率），前端按 pp 展示
                "weekOverWeekRate": (wc - wp)
                if wc is not None and wp is not None
                else None,
                "dayOverDayRate": (tv - y)
                if tv is not None and y is not None
                else None,
                "trend30d": _trend30d("grossMargin"),
            }

        cost_coverage = (
            (today_m["covered_revenue"] / today_m["revenue"])
            if today_m["revenue"] > 0
            else None
        )

        return {
            "revenue": _amount_metric("revenue"),
            "cost": _amount_metric("cost"),
            "grossProfit": _amount_metric("grossProfit"),
            "grossMargin": _margin_metric(),
            "costCoverageRate": cost_coverage,
        }

    @staticmethod
    async def _totals(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        inclusive: bool = False,
    ) -> Dict[str, float]:
        """窗口内收入 / 成本 / 毛利汇总；covered_revenue = 有成本运单的收入。"""
        wb_cost = ProfitService._wb_cost_subq()
        wb_rev = ProfitService._wb_rev_subq()

        revenue_expr = func.coalesce(wb_rev.c.rev, Waybill.freight_amount, 0)
        cost_expr = func.coalesce(wb_cost.c.cost, 0)
        end_clause = (
            Waybill.created_at <= end if inclusive else Waybill.created_at < end
        )

        stmt = (
            select(
                func.coalesce(func.sum(revenue_expr), 0).label("revenue"),
                func.coalesce(func.sum(cost_expr), 0).label("cost"),
                func.coalesce(
                    func.sum(
                        case((wb_cost.c.cost.isnot(None), revenue_expr), else_=0)
                    ),
                    0,
                ).label("covered_revenue"),
            )
            .select_from(Waybill)
            .outerjoin(wb_rev, wb_rev.c.waybill_id == Waybill.id)
            .outerjoin(wb_cost, wb_cost.c.waybill_id == Waybill.id)
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start,
                end_clause,
            )
        )
        row = (await db.execute(stmt)).one()
        revenue = _to_float(row.revenue)
        cost = _to_float(row.cost)
        return {
            "revenue": revenue,
            "cost": cost,
            "grossProfit": revenue - cost,
            "covered_revenue": _to_float(row.covered_revenue),
        }

    @staticmethod
    async def _daily_rows(
        db: AsyncSession, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """按自然日聚合收入/成本（含 end 时刻），用于近 30 日趋势。"""
        wb_cost = ProfitService._wb_cost_subq()
        wb_rev = ProfitService._wb_rev_subq()
        date_expr = func.date(Waybill.created_at).label("d")
        revenue_expr = func.coalesce(wb_rev.c.rev, Waybill.freight_amount, 0)
        cost_expr = func.coalesce(wb_cost.c.cost, 0)

        stmt = (
            select(
                date_expr,
                func.coalesce(func.sum(revenue_expr), 0).label("revenue"),
                func.coalesce(func.sum(cost_expr), 0).label("cost"),
            )
            .select_from(Waybill)
            .outerjoin(wb_rev, wb_rev.c.waybill_id == Waybill.id)
            .outerjoin(wb_cost, wb_cost.c.waybill_id == Waybill.id)
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start,
                Waybill.created_at <= end,
            )
            .group_by(date_expr)
            .order_by(date_expr.asc())
        )
        rows = (await db.execute(stmt)).all()
        return [
            {
                "date": str(r.d),
                "revenue": _to_float(r.revenue),
                "cost": _to_float(r.cost),
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 2. 收入 / 成本 / 毛利趋势
    # ------------------------------------------------------------------

    @staticmethod
    def _granularity_bucket(granularity: str):
        if granularity == "month":
            return func.date_format(Waybill.created_at, "%Y-%m")
        if granularity == "week":
            # 周一归桶
            return func.date_format(
                func.subdate(
                    Waybill.created_at, func.dayofweek(Waybill.created_at) - 1
                ),
                "%Y-%m-%d",
            )
        return func.date_format(Waybill.created_at, "%Y-%m-%d")

    @staticmethod
    async def trend(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        granularity: str = "day",
    ) -> List[Dict[str, Any]]:
        """按日/周/月聚合的收入、成本、毛利、毛利率。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        wb_cost = ProfitService._wb_cost_subq()
        wb_rev = ProfitService._wb_rev_subq()
        bucket = ProfitService._granularity_bucket(granularity)
        revenue_expr = func.coalesce(wb_rev.c.rev, Waybill.freight_amount, 0)
        cost_expr = func.coalesce(wb_cost.c.cost, 0)

        stmt = (
            select(
                bucket.label("bucket"),
                func.coalesce(func.sum(revenue_expr), 0).label("revenue"),
                func.coalesce(func.sum(cost_expr), 0).label("cost"),
            )
            .select_from(Waybill)
            .outerjoin(wb_rev, wb_rev.c.waybill_id == Waybill.id)
            .outerjoin(wb_cost, wb_cost.c.waybill_id == Waybill.id)
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(bucket)
            .order_by(bucket.asc())
        )
        rows = (await db.execute(stmt)).all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            revenue = _to_float(r.revenue)
            cost = _to_float(r.cost)
            out.append(
                {
                    "date": str(r.bucket),
                    "revenue": revenue,
                    "cost": cost,
                    "grossProfit": revenue - cost,
                    "grossMargin": _safe_margin(revenue, cost),
                }
            )
        return out

    # ------------------------------------------------------------------
    # 3. 承运结构（自有 / 承运商 / 社会运力）
    # ------------------------------------------------------------------

    @staticmethod
    async def carrier_structure(
        db: AsyncSession, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """按任务 carrier_type 汇总（成本按台数分摊，收入按台数在任务间分摊）。

        以 (运单, 任务) 挂接行为最小粒度：
          分摊成本  = tcr.total_cost_amount * twi.quantity / 任务总台数
          分摊收入  = 运单收入 * twi.quantity / 运单已调度台数
        仅统计已挂接任务（已调度）部分，反映各承运方式的成本与毛利贡献。
        """
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        task_qty = ProfitService._task_qty_subq()
        wb_rev = ProfitService._wb_rev_subq()

        # 运单已调度台数（收入分摊分母）
        wb_disp_qty = (
            select(
                TaskWaybillItem.waybill_id.label("waybill_id"),
                func.sum(TaskWaybillItem.quantity).label("disp_qty"),
            )
            .where(TaskWaybillItem.is_deleted == 0)
            .group_by(TaskWaybillItem.waybill_id)
            .subquery()
        )

        revenue_expr = func.coalesce(wb_rev.c.rev, Waybill.freight_amount, 0)
        alloc_cost = (
            TaskCostResult.total_cost_amount
            * TaskWaybillItem.quantity
            / func.nullif(task_qty.c.total_qty, 0)
        )
        alloc_rev = (
            revenue_expr
            * TaskWaybillItem.quantity
            / func.nullif(wb_disp_qty.c.disp_qty, 0)
        )

        stmt = (
            select(
                Task.carrier_type.label("carrier_type"),
                func.coalesce(func.sum(alloc_rev), 0).label("revenue"),
                func.coalesce(func.sum(alloc_cost), 0).label("cost"),
                func.coalesce(func.sum(TaskWaybillItem.quantity), 0).label(
                    "vehicle_quantity"
                ),
            )
            .select_from(TaskWaybillItem)
            .join(
                Waybill,
                and_(
                    Waybill.id == TaskWaybillItem.waybill_id,
                    Waybill.is_deleted == 0,
                    Waybill.created_at >= start_dt,
                    Waybill.created_at < end_dt,
                ),
            )
            .join(
                Task,
                and_(Task.id == TaskWaybillItem.task_id, Task.is_deleted == 0),
            )
            .join(task_qty, task_qty.c.task_id == TaskWaybillItem.task_id)
            .join(wb_disp_qty, wb_disp_qty.c.waybill_id == TaskWaybillItem.waybill_id)
            .join(
                TaskCostResult,
                and_(
                    TaskCostResult.task_id == TaskWaybillItem.task_id,
                    TaskCostResult.is_active == 1,
                    TaskCostResult.is_deleted == 0,
                ),
            )
            .outerjoin(wb_rev, wb_rev.c.waybill_id == TaskWaybillItem.waybill_id)
            .where(TaskWaybillItem.is_deleted == 0)
            .group_by(Task.carrier_type)
            .order_by(func.coalesce(func.sum(alloc_cost), 0).desc())
        )
        rows = (await db.execute(stmt)).all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            revenue = _to_float(r.revenue)
            cost = _to_float(r.cost)
            ct = int(r.carrier_type) if r.carrier_type is not None else -1
            out.append(
                {
                    "carrierType": ct,
                    "label": _CARRIER_TYPE_LABELS.get(ct, _UNKNOWN_LABEL),
                    "revenue": revenue,
                    "cost": cost,
                    "grossProfit": revenue - cost,
                    "grossMargin": _safe_margin(revenue, cost),
                    "vehicleQuantity": int(r.vehicle_quantity or 0),
                }
            )
        return out

    # ------------------------------------------------------------------
    # 4. 成本构成（按费用类型）
    # ------------------------------------------------------------------

    @staticmethod
    async def cost_structure(
        db: AsyncSession, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """按 fee_type 的成本费用项构成（同样按台数分摊到窗口内运单）。

        金额 = Σ ( 方向符号 * tcri.amount * twi.quantity / 任务总台数 )
        方向 1-加项(+) 2-扣减项(-)，净额之和 = 分摊成本总额。
        """
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        task_qty = ProfitService._task_qty_subq()

        signed_amount = case(
            (TaskCostResultItem.direction == 2, -TaskCostResultItem.amount),
            else_=TaskCostResultItem.amount,
        )
        alloc = (
            signed_amount
            * TaskWaybillItem.quantity
            / func.nullif(task_qty.c.total_qty, 0)
        )
        fee_name_expr = func.coalesce(
            TaskCostResultItem.fee_name, TaskCostResultItem.fee_type
        )

        stmt = (
            select(
                TaskCostResultItem.fee_type.label("fee_type"),
                fee_name_expr.label("fee_name"),
                func.coalesce(func.sum(alloc), 0).label("amount"),
            )
            .select_from(TaskCostResultItem)
            .join(
                TaskCostResult,
                and_(
                    TaskCostResult.id == TaskCostResultItem.result_id,
                    TaskCostResult.is_active == 1,
                    TaskCostResult.is_deleted == 0,
                ),
            )
            .join(
                TaskWaybillItem,
                and_(
                    TaskWaybillItem.task_id == TaskCostResultItem.task_id,
                    TaskWaybillItem.is_deleted == 0,
                ),
            )
            .join(task_qty, task_qty.c.task_id == TaskCostResultItem.task_id)
            .join(
                Waybill,
                and_(
                    Waybill.id == TaskWaybillItem.waybill_id,
                    Waybill.is_deleted == 0,
                    Waybill.created_at >= start_dt,
                    Waybill.created_at < end_dt,
                ),
            )
            .where(TaskCostResultItem.is_deleted == 0)
            .group_by(TaskCostResultItem.fee_type, fee_name_expr)
            .order_by(func.coalesce(func.sum(alloc), 0).desc())
        )
        rows = (await db.execute(stmt)).all()
        total = sum(_to_float(r.amount) for r in rows) or 0.0
        return [
            {
                "feeType": r.fee_type,
                "feeName": r.fee_name or r.fee_type,
                "amount": _to_float(r.amount),
                "share": (_to_float(r.amount) / total) if total > 0 else 0.0,
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 5. 客户毛利排行
    # ------------------------------------------------------------------

    @staticmethod
    async def customer_rank(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        limit: int = 10,
        sort_by: str = "profit",
    ) -> List[Dict[str, Any]]:
        """客户维度收入 / 成本 / 毛利 / 毛利率 TopN。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        limit = max(1, min(int(limit or 10), 5000))
        sort_key = (sort_by or "profit").strip().lower()
        if sort_key not in ("profit", "revenue", "margin"):
            sort_key = "profit"

        wb_cost = ProfitService._wb_cost_subq()
        wb_rev = ProfitService._wb_rev_subq()
        revenue_expr = func.coalesce(wb_rev.c.rev, Waybill.freight_amount, 0)
        cost_expr = func.coalesce(wb_cost.c.cost, 0)
        revenue_sum = func.coalesce(func.sum(revenue_expr), 0)
        cost_sum = func.coalesce(func.sum(cost_expr), 0)
        profit_sum = revenue_sum - cost_sum

        customer_name_expr = func.coalesce(
            Customer.customer_name, Waybill.customer_name, literal(_UNKNOWN_LABEL)
        )

        if sort_key == "revenue":
            order_expr = revenue_sum.desc()
        elif sort_key == "margin":
            # 毛利率排序：收入为 0 视为最低
            order_expr = case(
                (revenue_sum > 0, profit_sum / revenue_sum), else_=literal(-1)
            ).desc()
        else:
            order_expr = profit_sum.desc()

        stmt = (
            select(
                Waybill.customer_id.label("customer_id"),
                customer_name_expr.label("customer_name"),
                revenue_sum.label("revenue"),
                cost_sum.label("cost"),
                func.count(func.distinct(Waybill.id)).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
            )
            .select_from(Waybill)
            .outerjoin(wb_rev, wb_rev.c.waybill_id == Waybill.id)
            .outerjoin(wb_cost, wb_cost.c.waybill_id == Waybill.id)
            .outerjoin(
                Customer,
                and_(Customer.id == Waybill.customer_id, Customer.is_deleted == 0),
            )
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(Waybill.customer_id, customer_name_expr)
            .order_by(order_expr)
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            revenue = _to_float(r.revenue)
            cost = _to_float(r.cost)
            out.append(
                {
                    "customerId": r.customer_id,
                    "customerName": r.customer_name or _UNKNOWN_LABEL,
                    "revenue": revenue,
                    "cost": cost,
                    "grossProfit": revenue - cost,
                    "grossMargin": _safe_margin(revenue, cost),
                    "waybillCount": int(r.waybill_count or 0),
                    "vehicleQuantity": int(r.vehicle_quantity or 0),
                }
            )
        return out
