"""
经营驾驶舱（BI 看板）服务

提供 7 类聚合查询，全部基于租户业务库 `biz_waybill` 等表。
- KPI 总览 / 收入与单量趋势 / 客户排行 / 客户类型分布
- 起讫地区域排行 / 商品车品牌排行 / 运营效率

设计要点：
1. 所有时间筛选统一基于 `biz_waybill.created_at`
2. 软删除过滤：`is_deleted = 0`
3. 环比口径：对照期为等长滚动窗口（前一周期）
4. NULL 兜底：客户/客户类型/区域名/品牌名 为空时归入"未知"
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
    async def kpi_summary(
        db: AsyncSession,
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        """4 KPI + 环比 + sparkline。

        Returns:
            {
              "revenue": { value, previous, growthRate, sparkline:[{date, value}] },
              "waybillCount": { ... },
              "vehicleQuantity": { ... },
              "customerCount": { ... },
            }
        """
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        prev_start, prev_end = _previous_window(start_dt, end_dt)

        current = await CockpitService._kpi_totals(db, start_dt, end_dt)
        previous = await CockpitService._kpi_totals(db, prev_start, prev_end)
        sparkline = await CockpitService._kpi_sparkline(db, start_dt, end_dt)

        return {
            "revenue": {
                "value": current["revenue"],
                "previous": previous["revenue"],
                "growthRate": _safe_growth_rate(
                    current["revenue"], previous["revenue"]
                ),
                "sparkline": [
                    {"date": p["date"], "value": p["revenue"]} for p in sparkline
                ],
            },
            "waybillCount": {
                "value": current["waybill_count"],
                "previous": previous["waybill_count"],
                "growthRate": _safe_growth_rate(
                    current["waybill_count"], previous["waybill_count"]
                ),
                "sparkline": [
                    {"date": p["date"], "value": p["waybill_count"]}
                    for p in sparkline
                ],
            },
            "vehicleQuantity": {
                "value": current["vehicle_quantity"],
                "previous": previous["vehicle_quantity"],
                "growthRate": _safe_growth_rate(
                    current["vehicle_quantity"], previous["vehicle_quantity"]
                ),
                "sparkline": [
                    {"date": p["date"], "value": p["vehicle_quantity"]}
                    for p in sparkline
                ],
            },
            "customerCount": {
                "value": current["customer_count"],
                "previous": previous["customer_count"],
                "growthRate": _safe_growth_rate(
                    current["customer_count"], previous["customer_count"]
                ),
                "sparkline": [
                    {"date": p["date"], "value": p["customer_count"]}
                    for p in sparkline
                ],
            },
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
    async def _kpi_sparkline(
        db: AsyncSession, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """按日聚合的 sparkline；最多 30 天，过长会按天降采样到 ≤ 30 个点。"""
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
                Waybill.created_at < end,
            )
            .group_by(date_expr)
            .order_by(date_expr.asc())
        )
        rows = (await db.execute(stmt)).all()
        items = [
            {
                "date": str(r.d),
                "revenue": _to_float(r.revenue),
                "waybill_count": int(r.waybill_count or 0),
                "vehicle_quantity": int(r.vehicle_quantity or 0),
                "customer_count": int(r.customer_count or 0),
            }
            for r in rows
        ]
        # 超过 30 天降采样
        if len(items) > 30:
            step = len(items) / 30.0
            items = [items[int(i * step)] for i in range(30)]
        return items

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
    ) -> List[Dict[str, Any]]:
        """TopN 客户按运费贡献排序。"""
        start_dt = _coerce_dt(start)
        end_dt = _coerce_dt(end)
        limit = max(1, min(int(limit or 10), 50))

        # 客户名优先取 biz_customer.customer_name；NULL 时回退 biz_waybill.customer_name
        customer_name_expr = func.coalesce(
            Customer.customer_name, Waybill.customer_name, literal(_UNKNOWN_LABEL)
        )
        stmt = (
            select(
                Waybill.customer_id.label("customer_id"),
                customer_name_expr.label("customer_name"),
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
            .group_by(Waybill.customer_id, customer_name_expr)
            .order_by(func.coalesce(func.sum(Waybill.freight_amount), 0).desc())
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()

        # 计算总收入用于 share（基于本期全部运单）
        total_revenue = await CockpitService._sum_revenue(db, start_dt, end_dt)
        items: List[Dict[str, Any]] = []
        for r in rows:
            revenue = _to_float(r.revenue)
            items.append(
                {
                    "customerId": r.customer_id,
                    "customerName": r.customer_name or _UNKNOWN_LABEL,
                    "revenue": revenue,
                    "waybillCount": int(r.waybill_count or 0),
                    "vehicleQuantity": int(r.vehicle_quantity or 0),
                    "share": (revenue / total_revenue) if total_revenue > 0 else 0,
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
        """运单状态分布 + 计算异常率 + 锁定单数。"""
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

        # 计算状态 + 锁定数
        calc_stmt = select(
            func.count(Waybill.id).label("total"),
            func.sum(
                case((Waybill.calc_status == "exception", 1), else_=0)
            ).label("exception_count"),
            func.sum(case((Waybill.is_locked == 1, 1), else_=0)).label(
                "locked_count"
            ),
        ).where(
            Waybill.is_deleted == 0,
            Waybill.created_at >= start_dt,
            Waybill.created_at < end_dt,
        )
        row = (await db.execute(calc_stmt)).one()
        total = int(row.total or 0)
        exception_count = int(row.exception_count or 0)
        locked_count = int(row.locked_count or 0)
        exception_rate = (exception_count / total) if total > 0 else 0.0

        return {
            "statusDist": status_dist,
            "calcExceptionRate": exception_rate,
            "calcExceptionCount": exception_count,
            "lockedCount": locked_count,
            "totalCount": total,
        }
