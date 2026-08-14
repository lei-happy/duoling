"""经营核算 API（文档 13 §七）

接口前缀：``/api/client/finance/profit``

与 ``/insight/cockpit/profit`` 是**两个口径**：本组接口只认已对账确认的收入与已审批的
成本，按财务期间归期；驾驶舱用计费引擎理论值、按运单创建时间归期。差异说明由前端常驻
展示，不要试图让两边数字对平。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.profit_accounting import (
    AccountingKpiOut,
    DimensionRowOut,
    DrillDownOut,
    InterEntityOut,
)
from app.modules.client.services.finance.accounting.accounting_constants import (
    DIMENSION_LABELS,
    TAX_MODE_EXCL,
)
from app.modules.client.services.finance.accounting.profit_accounting_service import (
    ProfitAccountingService,
)

router = APIRouter()

_SVC = ProfitAccountingService


@router.get("/kpi")
async def kpi(
    period: Optional[str] = Query(
        default=None, description="YYYY-MM / YYYY-Qn / YYYY，默认本月",
    ),
    enterpriseId: Optional[int] = None,
    taxMode: str = Query(default=TAX_MODE_EXCL, description="incl-含税 excl-不含税"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """期间 KPI（财务确认口径）。"""
    data = await _SVC.kpi(
        db, period=period, enterprise_id=enterpriseId, tax_mode=taxMode,
    )
    return success(data=AccountingKpiOut(**data).model_dump())


@router.get("/dimensions")
async def list_dimensions(
    _: TokenData = Depends(get_current_user),
):
    """可用维度清单（前端 Tab 用）。"""
    return success(data=[
        {"value": k, "label": v} for k, v in DIMENSION_LABELS.items()
    ])


@router.get("/by-dimension")
async def by_dimension(
    dimension: str = Query(
        default="customer",
        description="customer / entity / route / vehicle / driver / carrier_type",
    ),
    period: Optional[str] = None,
    enterpriseId: Optional[int] = None,
    taxMode: str = Query(default=TAX_MODE_EXCL),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """按维度汇总收入成本毛利；未分摊成本单独成行。"""
    rows = await _SVC.by_dimension(
        db, dimension=dimension, period=period,
        enterprise_id=enterpriseId, tax_mode=taxMode,
    )
    return success(data={
        "list": [DimensionRowOut(**x).model_dump() for x in rows],
        "count": len(rows),
    })


@router.get("/drill-down")
async def drill_down(
    dimension: str = Query(...),
    dimensionValue: str = Query(...),
    period: Optional[str] = None,
    enterpriseId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """下钻：该维度值下的收入单据与成本单据清单。"""
    data = await _SVC.drill_down(
        db, dimension=dimension, dimension_value=dimensionValue,
        period=period, enterprise_id=enterpriseId,
    )
    return success(data=DrillDownOut(**data).model_dump())


@router.get("/inter-entity")
async def inter_entity(
    period: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """跨主体待结转明细（本期只呈现规模，不生成结算单据）。"""
    data = await _SVC.inter_entity(db, period=period)
    return success(data=InterEntityOut(**data).model_dump())


@router.get("/export")
async def export_worksheet(
    period: Optional[str] = None,
    enterpriseId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """底稿导出：收入单据 + 成本单据两张表页。"""
    data = await _SVC.build_export_workbook(
        db, period=period, enterprise_id=enterpriseId,
    )
    _, _, label = _SVC.parse_period(period)
    filename = f"accounting_{(period or label).replace(' ', '')}.xlsx"
    return StreamingResponse(
        iter([data]),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
