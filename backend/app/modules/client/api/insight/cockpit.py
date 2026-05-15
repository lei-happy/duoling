"""
企业端经营驾驶舱（BI 看板）API

提供 7 个聚合查询接口，前端按需调用。所有接口均要求登录态，按租户库隔离。

公共查询参数：
  - start: 起始时间（datetime；ISO 字符串），未传则默认本月 1 号 00:00
  - end:   截止时间（datetime；ISO 字符串），未传则默认现在
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.services.insight.cockpit_service import CockpitService


router = APIRouter()


def _resolve_window(
    start: Optional[datetime], end: Optional[datetime]
) -> tuple[datetime, datetime]:
    """默认窗口：本月 1 号 00:00 → 现在。"""
    now = datetime.now()
    if end is None:
        end_dt = now
    else:
        end_dt = end
    if start is None:
        start_dt = end_dt.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
    else:
        start_dt = start
    # 兜底：start >= end 时挪到 end 前一秒，避免空区间报错
    if start_dt >= end_dt:
        start_dt = end_dt
    return start_dt, end_dt


@router.get("/kpi-summary")
async def kpi_summary(
    start: Optional[datetime] = Query(None, description="起始时间"),
    end: Optional[datetime] = Query(None, description="截止时间"),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """核心 KPI 卡片：当日值、近 30 日趋势、周同比 + 日同比（与 start/end 无关，兼容入参）"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await CockpitService.kpi_summary(db, start_dt, end_dt)
    return success(data=data)


@router.get("/revenue-trend")
async def revenue_trend(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    granularity: str = Query(
        "day", description="聚合粒度: day | week | month"
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """收入与单量趋势"""
    start_dt, end_dt = _resolve_window(start, end)
    if granularity not in ("day", "week", "month"):
        granularity = "day"
    data = await CockpitService.revenue_trend(db, start_dt, end_dt, granularity)
    return success(data=data)


@router.get("/customer-rank")
async def customer_rank(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=5000, description="返回条数上限，最大 5000"),
    sort_by: str = Query(
        "revenue",
        description="排序字段: revenue（运费收入）| vehicle_quantity（商品车台数）",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """客户运费贡献排行"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await CockpitService.customer_rank(
        db, start_dt, end_dt, limit, sort_by=sort_by
    )
    return success(data=data)


@router.get("/customer-type-dist")
async def customer_type_dist(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """客户类型分布"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await CockpitService.customer_type_dist(db, start_dt, end_dt)
    return success(data=data)


@router.get("/region-rank")
async def region_rank(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    type: str = Query("origin", description="origin | destination"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """起讫地排行"""
    start_dt, end_dt = _resolve_window(start, end)
    t = type if type in ("origin", "destination") else "origin"
    data = await CockpitService.region_rank(db, start_dt, end_dt, t, limit)
    return success(data=data)


@router.get("/vehicle-brand-rank")
async def vehicle_brand_rank(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """商品车品牌排行"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await CockpitService.vehicle_brand_rank(db, start_dt, end_dt, limit)
    return success(data=data)


@router.get("/operation-efficiency")
async def operation_efficiency(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """运营效率（状态分布 + 计算异常率 + 锁定数）"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await CockpitService.operation_efficiency(db, start_dt, end_dt)
    return success(data=data)
