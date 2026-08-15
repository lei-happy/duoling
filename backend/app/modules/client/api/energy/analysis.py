from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.services.energy.analysis_service import EnergyAnalysisService

router = APIRouter()


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyAnalysisService.overview(db))


@router.get("/vehicle-cost")
async def vehicle_cost(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    end = end or date.today()
    start = start or (end - timedelta(days=30))
    return success(data=await EnergyAnalysisService.vehicle_cost(db, start, end))


@router.get("/supplier-compare")
async def supplier_compare(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    end = end or date.today()
    start = start or (end - timedelta(days=30))
    return success(data=await EnergyAnalysisService.supplier_compare(db, start, end))


@router.get("/fund-efficiency/{account_id}")
async def fund_efficiency(
    account_id: int,
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyAnalysisService.fund_efficiency(db, account_id, days))
