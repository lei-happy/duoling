from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.schemas.energy.consumption import (
    EnergyConsumptionAssignIn,
    EnergyConsumptionCreate,
    EnergyConsumptionOut,
)
from app.modules.client.services.energy.consumption_service import EnergyConsumptionService

router = APIRouter()


@router.get("")
async def page_consumptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    accountId: Optional[int] = None,
    energyType: Optional[str] = None,
    matchStatus: Optional[str] = None,
    sourceChannel: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyConsumptionService.page(
        db, page, page_size, keyword, accountId, energyType,
        matchStatus, sourceChannel, start, end,
    ))


@router.post("")
@operation_log(module="能源消费", action="录入", description="手工录入能源消费")
async def create_consumption(
    data: EnergyConsumptionCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyConsumptionService.create_manual(db, data)
    return success(data=EnergyConsumptionOut.from_model(obj).model_dump())


@router.post("/{cid}/assign")
@operation_log(module="能源消费", action="归属", description="人工归属车辆/司机")
async def assign_consumption(
    cid: int,
    data: EnergyConsumptionAssignIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyConsumptionService.assign(db, cid, data)
    return success(data=EnergyConsumptionOut.from_model(obj).model_dump())
