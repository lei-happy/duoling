from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.energy.account import (
    EnergyAccountCreate,
    EnergyAccountOut,
    EnergyAccountUpdate,
    EnergyAdjustIn,
    EnergyTxnOut,
)
from app.modules.client.services.energy.account_service import EnergyAccountService

router = APIRouter()


@router.get("")
async def page_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    supplierId: Optional[int] = None,
    energyType: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyAccountService.page(
        db, page, page_size, keyword, supplierId, energyType, status,
    ))


@router.get("/{aid}")
async def get_account(
    aid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyAccountService.get(db, aid)
    return success(data=EnergyAccountOut.from_model(obj).model_dump())


@router.post("")
@operation_log(module="能源账户", action="新增", description="新增能源账户")
async def create_account(
    data: EnergyAccountCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyAccountService.create(db, data)
    return success(data=EnergyAccountOut.from_model(obj).model_dump())


@router.put("/{aid}")
@operation_log(module="能源账户", action="编辑", description="编辑能源账户")
async def update_account(
    aid: int,
    data: EnergyAccountUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyAccountService.update(db, aid, data)
    return success(data=EnergyAccountOut.from_model(obj).model_dump())


@router.delete("/{aid}")
@operation_log(module="能源账户", action="删除", description="删除能源账户")
async def delete_account(
    aid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyAccountService.delete(db, aid)
    return success()


@router.get("/{aid}/txns")
async def page_txns(
    aid: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    txnType: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyAccountService.page_txns(
        db, aid, page, page_size, txnType,
    ))


@router.post("/{aid}/adjust")
@operation_log(module="能源账户", action="调账", description="能源账户调账")
async def adjust_account(
    aid: int,
    data: EnergyAdjustIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    txn = await EnergyAccountService.adjust(
        db, aid, data,
        operator_id=current_user.user_id,
        operator_name=getattr(current_user, "nickname", None),
    )
    return success(data=EnergyTxnOut.from_model(txn).model_dump())
