"""
经营驾驶舱（BI 看板）服务

提供 7 类聚合查询，全部基于租户业务库 `biz_waybill` 等表。
- KPI 总览 / 收入与单量趋势 / 客户排行 / 客户类型分布
- 起讫地区域排行 / 商品车品牌排行 / 运营效率

设计要点：
1. 所有时间筛选统一基于 `biz_waybill.created_at`
2. 软删除过滤：`is_deleted = 0`
3. 顶部 KPI 卡片：自然日口径（当日值 + 近 30 天趋势）；对比区为周同比（本周一 0 点至今 vs 上周一 0 点起相同时长）与日同比（今天 0 点至今 vs 昨天 0 点至昨天同一时刻）
4. 其余图表接口：仍使用请求参数 `start`/`end` 窗口；环比口径见各接口说明
5. NULL 兜底：客户/客户类型/区域名/品牌名 为空时归入"未知"
"""

from __future__ import annotations

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, case, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import BizVehicleBrand
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo


# ---------------------------------------------------------------------------
# 静态字典
# ---------------------------------------------------------------------------

_CUSTOMER_TYPE_LABELS = {
    0: "主机厂",
    1: "贸易商",
    2: "经销商",
    3: "个人",
    4: "其他",
}

_WAYBILL_STATUS_LABELS = {
    0: "待确认",
    1: "已确认",
    2: "已调度",
    3: "运输中",
    4: "已送达",
    5: "已完成",
    6: "已取消",
}

# 运单运费计算状态（biz_waybill.calc_status）
_CALC_STATUS_LABELS = {
    "pending": "待计算",
    "calculating": "计算中",
    "calculated": "已计算",
    "exception": "计算异常",
    "locked": "计算锁定",
}
_CALC_STATUS_ORDER = (
    "pending",
    "calculating",
    "calculated",
    "exception",
    "locked",
)

_UNKNOWN_LABEL = "未知"


def _to_float(value: Any) -> float:
    """Decimal/None/数字 → float（None 视为 0）。"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _safe_growth_rate(current: float, previous: float) -> Optional[float]:
    """
    环比增长率：
    - previous = 0 时返回 None（无法计算，前端显示 "—"）
    - 否则返回 (current - previous) / previous
    """
    if previous == 0:
        return None
    return (current - previous) / previous


def _previous_window(start: datetime, end: datetime) -> Tuple[datetime, datetime]:
    """等长滚动窗口的前一期。"""
    delta = end - start
    return start - delta, start


def _coerce_dt(value: Any) -> datetime:
    """date → datetime；datetime 透传；其他抛错由调用方处理。"""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    raise TypeError(f"Unsupported datetime type: {type(value)}")


# ---------------------------------------------------------------------------
# 主服务
# ---------------------------------------------------------------------------


class CockpitService:
    """经营驾驶舱聚合查询服务"""

    # ---------- 1. 核心 KPI ----------

    @staticmethod
    def _week_monday_start(d: date) -> datetime:
        """自然周：周一 00:00:00（date.weekday(): 周一=0）。"""
        monday = d - timedelta(days=d.weekday())
        return datetime.combine(monday, datetime.min.time())

    @staticmethod
    async def kpi_summary(
        db: AsyncSession,
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        """4 KPI 卡片：当日累计、近 30 日趋势、周同比 + 日同比。

        说明：`start`/`end` 为接口兼容保留，本期卡片数据**不依赖**该窗口，
        一律按服务端当前时刻聚合。

        周同比：本周一 0 点～当前时刻 vs 上周一 0 点～（上周一 + 与本周已过的相同时长）。
        日同比：今天 0 点～当前时刻 vs 昨天 0 点～当前时刻的前一天同一时刻。

        Returns:
            {
              "revenue": {
                todayValue, weekOverWeekRate, dayOverDayRate,
                trend30d: [{date, value}],
              },
              ...
            }
        """
        _ = (start, end)  # 兼容入参；本期 KPI 卡片不按该窗口计算

        now = datetime.now()
        today_d = now.date()
        today_start = datetime.combine(today_d, datetime.min.time())
        yesterday_d = today_d - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday_d, datetime.min.time())
        trend_start = datetime.combine(today_d - timedelta(days=29), datetime.min.time())

        today_m = await CockpitService._kpi_totals_inclusive_end(
            db, today_start, now
        )
        yesterday_same_m = await CockpitService._kpi_totals_inclusive_end(
            db, yesterday_start, now - timedelta(days=1)
        )

        this_monday = CockpitService._week_monday_start(today_d)
        last_monday = this_monday - timedelta(days=7)
        span_from_this_monday = now - this_monday
        last_week_slice_end = last_monday + span_from_this_monday
        this_week_m = await CockpitService._kpi_totals_inclusive_end(
            db, this_monday, now
        )
        last_week_slice_m = await CockpitService._kpi_totals_inclusive_end(
            db, last_monday, last_week_slice_end
        )

        daily_rows = await CockpitService._kpi_daily_rows_inclusive_end(
            db, trend_start, now
        )

        def _fill_trend30d(field: str) -> List[Dict[str, Any]]:
            by_d: Dict[str, Dict[str, Any]] = {
                str(r["date"]): r for r in daily_rows
            }
            out: List[Dict[str, Any]] = []
            for i in range(30):
                d = today_d - timedelta(days=29 - i)
                key = str(d)
                row = by_d.get(key)
                if row:
                    v = row[field]
                else:
                    v = 0.0 if field == "revenue" else 0
                out.append({"date": key, "value": float(v) if field == "revenue" else int(v)})
            return out

        def _pack_metric(trend_field: str) -> Dict[str, Any]:
            tv = (
                float(today_m[trend_field])
                if trend_field == "revenue"
                else int(today_m[trend_field])
            )
            y_same = (
                float(yesterday_same_m[trend_field])
                if trend_field == "revenue"
                else int(yesterday_same_m[trend_field])
            )
            w_cur = (
                float(this_week_m[trend_field])
                if trend_field == "revenue"
                else int(this_week_m[trend_field])
            )
            w_prev = (
                float(last_week_slice_m[trend_field])
                if trend_field == "revenue"
                else int(last_week_slice_m[trend_field])
            )
            return {
                "todayValue": tv,
                "weekOverWeekRate": _safe_growth_rate(float(w_cur), float(w_prev)),
                "dayOverDayRate": _safe_growth_rate(float(tv), float(y_same)),
                "trend30d": _fill_trend30d(trend_field),
            }

        return {
            "revenue": _pack_metric("revenue"),
            "waybillCount": _pack_metric("waybill_count"),
            "vehicleQuantity": _pack_metric("vehicle_quantity"),
            "customerCount": _pack_metric("customer_count"),
        }

    @staticmethod
    async def _kpi_totals(
        db: AsyncSession, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        stmt = (
            select(
                func.coalesce(func.sum(Waybill.freight_amount), 0).label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
                func.count(func.distinct(Waybill.customer_id)).label(
                    "customer_count"
                ),
            )
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start,
                Waybill.created_at < end,
            )
        )
        row = (await db.execute(stmt)).one()
        return {
            "revenue": _to_float(row.revenue),
            "waybill_count": int(row.waybill_count or 0),
            "vehicle_quantity": int(row.vehicle_quantity or 0),
            "customer_count": int(row.customer_count or 0),
        }

    @staticmethod
    async def _kpi_totals_inclusive_end(
        db: AsyncSession, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        """与 _kpi_totals 相同聚合，右边界为闭区间（含 end 时刻）。"""
        stmt = (
            select(
                func.coalesce(func.sum(Waybill.freight_amount), 0).label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
                func.count(func.distinct(Waybill.customer_id)).label(
                    "customer_count"
                ),
            )
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start,
                Waybill.created_at <= end,
            )
        )
        row = (await db.execute(stmt)).one()
        return {
            "revenue": _to_float(row.revenue),
            "waybill_count": int(row.waybill_count or 0),
            "vehicle_quantity": int(row.vehicle_quantity or 0),
            "customer_count": int(row.customer_count or 0),
        }

    @staticmethod
    async def _kpi_daily_rows_inclusive_end(
        db: AsyncSession, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """按自然日聚合多指标，含 end 时刻前数据；用于近 30 日趋势。"""
        date_expr = func.date(Waybill.created_at).label("d")
        stmt = (
            select(
                date_expr,
                func.coalesce(func.sum(Waybill.freight_amount), 0).label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
                func.count(func.distinct(Waybill.customer_id)).label(
                    "customer_count"
                ),
            )
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
                "waybill_count": int(r.waybill_count or 0),
                "vehicle_quantity": int(r.vehicle_quantity or 0),
                "customer_count": int(r.customer_count or 0),
            }
            for r in rows
        ]

    # ---------- 2. 收入与单量趋势 ----------

    @staticmethod
    async def revenue_trend(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        granularity: str = "day",
    ) -> List[Dict[str, Any]]:
        """按日/周/月聚合的收入和单量。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)

        bucket_expr = CockpitService._granularity_bucket(granularity)
        stmt = (
            select(
                bucket_expr.label("bucket"),
                func.coalesce(func.sum(Waybill.freight_amount), 0).label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
            )
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(bucket_expr)
            .order_by(bucket_expr.asc())
        )
        rows = (await db.execute(stmt)).all()
        return [
            {
                "date": str(r.bucket),
                "revenue": _to_float(r.revenue),
                "waybillCount": int(r.waybill_count or 0),
                "vehicleQuantity": int(r.vehicle_quantity or 0),
            }
            for r in rows
        ]

    @staticmethod
    def _granularity_bucket(granularity: str):
        """根据粒度返回 MySQL DATE_FORMAT 表达式。"""
        if granularity == "month":
            return func.date_format(Waybill.created_at, "%Y-%m")
        if granularity == "week":
            # 用 YEARWEEK(date, 3) ISO 周；返回如 '202620'
            return func.date_format(
                func.subdate(
                    Waybill.created_at,
                    func.dayofweek(Waybill.created_at) - 1,
                ),
                "%Y-%m-%d",
            )
        # 默认 day
        return func.date_format(Waybill.created_at, "%Y-%m-%d")

    # ---------- 3. TopN 客户 ----------

    @staticmethod
    async def customer_rank(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        limit: int = 10,
        sort_by: str = "revenue",
        customer_type: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """TopN 客户：默认按运费收入排序，可选按商品车台数排序。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        limit = max(1, min(int(limit or 10), 5000))
        sort_key = (sort_by or "revenue").strip().lower()
        if sort_key in ("vehicle_quantity", "vehiclequantity", "qty"):
            sort_key = "vehicle_quantity"
        else:
            sort_key = "revenue"

        # 客户名优先取 biz_customer.customer_name；NULL 时回退 biz_waybill.customer_name
        customer_name_expr = func.coalesce(
            Customer.customer_name, Waybill.customer_name, literal(_UNKNOWN_LABEL)
        )
        type_expr = func.coalesce(Customer.customer_type, literal(-1))
        revenue_sum = func.coalesce(func.sum(Waybill.freight_amount), 0)
        vehicle_sum = func.coalesce(func.sum(Waybill.quantity), 0)
        order_expr = vehicle_sum.desc() if sort_key == "vehicle_quantity" else revenue_sum.desc()

        where_clauses = [
            Waybill.is_deleted == 0,
            Waybill.created_at >= start_dt,
            Waybill.created_at < end_dt,
        ]
        if customer_type is not None:
            where_clauses.append(type_expr == int(customer_type))

        stmt = (
            select(
                Waybill.customer_id.label("customer_id"),
                customer_name_expr.label("customer_name"),
                revenue_sum.label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                vehicle_sum.label("vehicle_quantity"),
            )
            .select_from(Waybill)
            .outerjoin(
                Customer,
                and_(Customer.id == Waybill.customer_id, Customer.is_deleted == 0),
            )
            .where(*where_clauses)
            .group_by(Waybill.customer_id, customer_name_expr)
            .order_by(order_expr)
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()

        total_revenue = await CockpitService._sum_revenue(db, start_dt, end_dt)
        total_vehicles = await CockpitService._sum_vehicle_quantity(db, start_dt, end_dt)
        items: List[Dict[str, Any]] = []
        for r in rows:
            revenue = _to_float(r.revenue)
            vqty = int(r.vehicle_quantity or 0)
            if sort_key == "vehicle_quantity":
                share = (vqty / total_vehicles) if total_vehicles > 0 else 0.0
            else:
                share = (revenue / total_revenue) if total_revenue > 0 else 0.0
            items.append(
                {
                    "customerId": r.customer_id,
                    "customerName": r.customer_name or _UNKNOWN_LABEL,
                    "revenue": revenue,
                    "waybillCount": int(r.waybill_count or 0),
                    "vehicleQuantity": vqty,
                    "share": share,
                }
            )
        return items

    @staticmethod
    async def _sum_revenue(
        db: AsyncSession, start: datetime, end: datetime
    ) -> float:
        stmt = select(
            func.coalesce(func.sum(Waybill.freight_amount), 0)
        ).where(
            Waybill.is_deleted == 0,
            Waybill.created_at >= start,
            Waybill.created_at < end,
        )
        return _to_float((await db.execute(stmt)).scalar())

    @staticmethod
    async def _sum_vehicle_quantity(
        db: AsyncSession, start: datetime, end: datetime
    ) -> int:
        stmt = select(
            func.coalesce(func.sum(Waybill.quantity), 0)
        ).where(
            Waybill.is_deleted == 0,
            Waybill.created_at >= start,
            Waybill.created_at < end,
        )
        row = (await db.execute(stmt)).scalar()
        return int(row or 0)

    # ---------- 4. 客户类型分布 ----------

    @staticmethod
    async def customer_type_dist(
        db: AsyncSession,
        start: datetime,
        end: datetime,
    ) -> List[Dict[str, Any]]:
        """按客户类型聚合（NULL → -1 未知）。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)

        # 客户类型：取 biz_customer.customer_type；NULL 时归为 -1
        type_expr = func.coalesce(Customer.customer_type, literal(-1))

        stmt = (
            select(
                type_expr.label("customer_type"),
                func.coalesce(func.sum(Waybill.freight_amount), 0).label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
            )
            .select_from(Waybill)
            .outerjoin(
                Customer,
                and_(Customer.id == Waybill.customer_id, Customer.is_deleted == 0),
            )
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(type_expr)
            .order_by(func.coalesce(func.sum(Waybill.freight_amount), 0).desc())
        )
        rows = (await db.execute(stmt)).all()
        return [
            {
                "customerType": int(r.customer_type)
                if r.customer_type is not None
                else -1,
                "label": _CUSTOMER_TYPE_LABELS.get(int(r.customer_type), _UNKNOWN_LABEL)
                if r.customer_type is not None and int(r.customer_type) != -1
                else _UNKNOWN_LABEL,
                "revenue": _to_float(r.revenue),
                "waybillCount": int(r.waybill_count or 0),
                "vehicleQuantity": int(r.vehicle_quantity or 0),
            }
            for r in rows
        ]

    # ---------- 5. 区域排行 ----------

    @staticmethod
    async def region_rank(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        type_: str = "origin",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """起讫地排行（按 region_id 关联回省名，NULL 时按文本聚合）。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        limit = max(1, min(int(limit or 10), 50))

        if type_ == "destination":
            region_id_col = Waybill.destination_region_id
            text_col = Waybill.destination
        else:
            region_id_col = Waybill.origin_region_id
            text_col = Waybill.origin

        # 关联回省（level=1 的祖先）：
        # 简化为 biz_region 直接 JOIN——若数据已是省/市/区，则按 region.parent_code 回溯一次。
        # 这里采用简化策略：region 本身名字作为分组键，未匹配时使用 text_col。
        region_name_expr = func.coalesce(BizRegion.name, text_col, literal(_UNKNOWN_LABEL))

        stmt = (
            select(
                region_name_expr.label("region_name"),
                BizRegion.code.label("region_code"),
                BizRegion.level.label("region_level"),
                func.coalesce(func.sum(Waybill.freight_amount), 0).label("revenue"),
                func.count(Waybill.id).label("waybill_count"),
                func.coalesce(func.sum(Waybill.quantity), 0).label(
                    "vehicle_quantity"
                ),
            )
            .select_from(Waybill)
            .outerjoin(
                BizRegion,
                and_(BizRegion.id == region_id_col, BizRegion.is_deleted == 0),
            )
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(region_name_expr, BizRegion.code, BizRegion.level)
            .order_by(func.coalesce(func.sum(Waybill.freight_amount), 0).desc())
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()
        return [
            {
                "regionName": r.region_name or _UNKNOWN_LABEL,
                "regionCode": r.region_code,
                "regionLevel": int(r.region_level) if r.region_level is not None else None,
                "revenue": _to_float(r.revenue),
                "waybillCount": int(r.waybill_count or 0),
                "vehicleQuantity": int(r.vehicle_quantity or 0),
            }
            for r in rows
        ]

    # ---------- 6. 商品车品牌排行 ----------

    @staticmethod
    async def vehicle_brand_rank(
        db: AsyncSession,
        start: datetime,
        end: datetime,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """商品车品牌排行：按 biz_waybill_cargo 聚合，JOIN biz_waybill 过滤时间和软删。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        limit = max(1, min(int(limit or 20), 100))

        # 品牌名优先 brand_name_cn，否则 cargo.vehicle_brand 文本
        brand_name_expr = func.coalesce(
            BizVehicleBrand.brand_name_cn,
            WaybillCargo.vehicle_brand,
            literal(_UNKNOWN_LABEL),
        )

        stmt = (
            select(
                WaybillCargo.brand_id.label("brand_id"),
                brand_name_expr.label("brand_name"),
                func.coalesce(func.sum(WaybillCargo.quantity), 0).label(
                    "vehicle_quantity"
                ),
                func.count(func.distinct(WaybillCargo.waybill_id)).label(
                    "waybill_count"
                ),
            )
            .select_from(WaybillCargo)
            .join(
                Waybill,
                and_(Waybill.id == WaybillCargo.waybill_id, Waybill.is_deleted == 0),
            )
            .outerjoin(
                BizVehicleBrand,
                BizVehicleBrand.brand_id == WaybillCargo.brand_id,
            )
            .where(
                WaybillCargo.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(WaybillCargo.brand_id, brand_name_expr)
            .order_by(func.coalesce(func.sum(WaybillCargo.quantity), 0).desc())
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()
        # 计算总台数用于 share
        total_quantity = sum(int(r.vehicle_quantity or 0) for r in rows) or 0
        return [
            {
                "brandId": r.brand_id,
                "brandName": r.brand_name or _UNKNOWN_LABEL,
                "vehicleQuantity": int(r.vehicle_quantity or 0),
                "waybillCount": int(r.waybill_count or 0),
                "share": (int(r.vehicle_quantity or 0) / total_quantity)
                if total_quantity > 0
                else 0,
            }
            for r in rows
        ]

    # ---------- 7. 运营效率 ----------

    @staticmethod
    async def operation_efficiency(
        db: AsyncSession,
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        """运单状态分布 + 运费计算状态分布 + 锁定单数。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)

        # 状态分布
        status_stmt = (
            select(Waybill.status, func.count(Waybill.id).label("c"))
            .where(
                Waybill.is_deleted == 0,
                Waybill.created_at >= start_dt,
                Waybill.created_at < end_dt,
            )
            .group_by(Waybill.status)
        )
        status_rows = (await db.execute(status_stmt)).all()
        status_dist = [
            {
                "status": int(r.status),
                "label": _WAYBILL_STATUS_LABELS.get(
                    int(r.status), f"状态{r.status}"
                ),
                "count": int(r.c or 0),
            }
            for r in status_rows
        ]
        status_dist.sort(key=lambda x: x["status"])

        base_wb = and_(
            Waybill.is_deleted == 0,
            Waybill.created_at >= start_dt,
            Waybill.created_at < end_dt,
        )

        # 按运单 calc_status 分布（与「异常率」旧口径解耦，避免与业务状态混淆）
        calc_status_stmt = (
            select(Waybill.calc_status, func.count(Waybill.id).label("c"))
            .where(base_wb)
            .group_by(Waybill.calc_status)
        )
        calc_rows = (await db.execute(calc_status_stmt)).all()
        count_by_status: Dict[str, int] = {}
        for r in calc_rows:
            key = (r.calc_status or "pending").strip() or "pending"
            count_by_status[key] = int(r.c or 0)
        total = sum(count_by_status.values())

        locked_stmt = select(
            func.sum(case((Waybill.is_locked == 1, 1), else_=0)).label(
                "locked_count"
            ),
        ).where(base_wb)
        locked_row = (await db.execute(locked_stmt)).one()
        locked_count = int(locked_row.locked_count or 0)

        exception_count = int(count_by_status.get("exception", 0))
        exception_rate = (exception_count / total) if total > 0 else 0.0

        def _calc_status_label(k: str) -> str:
            return _CALC_STATUS_LABELS.get(k, f"状态({k})")

        seen_keys: set[str] = set()
        calc_status_dist: List[Dict[str, Any]] = []
        for k in _CALC_STATUS_ORDER:
            if k not in count_by_status:
                continue
            c = count_by_status[k]
            calc_status_dist.append(
                {"calcStatus": k, "label": _calc_status_label(k), "count": c}
            )
            seen_keys.add(k)
        for k in sorted(count_by_status.keys()):
            if k in seen_keys:
                continue
            c = count_by_status[k]
            calc_status_dist.append(
                {"calcStatus": k, "label": _calc_status_label(k), "count": c}
            )

        return {
            "statusDist": status_dist,
            "calcStatusDist": calc_status_dist,
            "calcExceptionRate": exception_rate,
            "calcExceptionCount": exception_count,
            "lockedCount": locked_count,
            "totalCount": total,
        }
