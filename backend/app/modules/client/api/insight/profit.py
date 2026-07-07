"""
企业端经营驾驶舱 - 利润总览（老板视角收入成本 BI）API

提供 5 个聚合查询接口，全部要求登录态并按租户库隔离。收入取计算引擎结果
（biz_waybill_freight_result），成本取 biz_task_cost_result 并按台数分摊到运单，
统一按 biz_waybill.created_at 归期。

公共查询参数：
  - start: 起始时间（datetime；未传默认本月 1 号 00:00）
  - end:   截止时间（datetime；未传默认现在）
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.services.insight.profit_service import ProfitService


router = APIRouter()


def _resolve_window(
    start: Optional[datetime], end: Optional[datetime]
) -> tuple[datetime, datetime]:
    """默认窗口：本月 1 号 00:00 → 现在（与运单总览一致）。"""
    now = datetime.now()
    end_dt = now if end is None else end
    if start is None:
        start_dt = end_dt.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
    else:
        start_dt = start
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
    """核心 KPI：收入 / 成本 / 毛利 / 毛利率（当日值 + 近 30 日趋势 + 周同比 + 日同比）"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await ProfitService.kpi_summary(db, start_dt, end_dt)
    return success(data=data)


@router.get("/trend")
async def trend(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    granularity: str = Query("day", description="聚合粒度: day | week | month"),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """收入 / 成本 / 毛利 / 毛利率趋势"""
    start_dt, end_dt = _resolve_window(start, end)
    if granularity not in ("day", "week", "month"):
        granularity = "day"
    data = await ProfitService.trend(db, start_dt, end_dt, granularity)
    return success(data=data)


@router.get("/carrier-structure")
async def carrier_structure(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """承运结构：按自有 / 承运商 / 社会运力汇总收入、成本、毛利"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await ProfitService.carrier_structure(db, start_dt, end_dt)
    return success(data=data)


@router.get("/cost-structure")
async def cost_structure(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """成本构成：按费用类型（fee_type）拆分分摊成本"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await ProfitService.cost_structure(db, start_dt, end_dt)
    return success(data=data)


@router.get("/customer-rank")
async def customer_rank(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=5000, description="返回条数上限，最大 5000"),
    sort_by: str = Query(
        "profit",
        description="排序字段: profit（毛利）| revenue（收入）| margin（毛利率）",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """客户毛利排行"""
    start_dt, end_dt = _resolve_window(start, end)
    data = await ProfitService.customer_rank(
        db, start_dt, end_dt, limit, sort_by=sort_by
    )
    return success(data=data)
