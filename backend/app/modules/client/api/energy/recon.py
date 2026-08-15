from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.services.energy.recon_service import EnergyReconService

router = APIRouter()


class BalanceReconIn(BaseModel):
    accountId: int
    supplierBalance: Decimal


class ConsumptionReconIn(BaseModel):
    accountId: Optional[int] = None
    supplierId: Optional[int] = None
    start: datetime
    end: datetime
    externalRows: list[dict]


class ItemProcessIn(BaseModel):
    processStatus: str = "confirmed"


@router.get("")
async def page_recons(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    accountId: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyReconService.page(db, page, page_size, accountId, status))


@router.get("/{rid}/items")
async def recon_items(
    rid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyReconService.items(db, rid))


@router.post("/balance")
@operation_log(module="能源对账", action="余额对账", description="创建账户余额对账")
async def create_balance(
    data: BalanceReconIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    obj = await EnergyReconService.create_balance_recon(
        db, data.accountId, data.supplierBalance, created_by=current_user.user_id,
    )
    return success(data={"id": obj.id, "differenceAmount": obj.difference_amount})


@router.post("/consumption")
@operation_log(module="能源对账", action="流水对账", description="创建消费流水对账")
async def create_consumption(
    data: ConsumptionReconIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    obj = await EnergyReconService.create_consumption_recon(
        db,
        account_id=data.accountId,
        supplier_id=data.supplierId,
        start=data.start,
        end=data.end,
        external_rows=data.externalRows,
        created_by=current_user.user_id,
    )
    return success(data={"id": obj.id, "diffCount": obj.diff_count})


@router.post("/items/{item_id}/process")
@operation_log(module="能源对账", action="处理差异", description="确认或忽略对账差异")
async def process_item(
    item_id: int,
    data: ItemProcessIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyReconService.confirm_item(db, item_id, data.processStatus)
    return success()


@router.post("/{rid}/settle")
@operation_log(module="能源对账", action="核销", description="确认对账单")
async def settle_recon(
    rid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyReconService.settle(db, rid)
    return success()
