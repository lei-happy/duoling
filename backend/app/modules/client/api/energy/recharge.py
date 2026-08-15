from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.energy.recharge import (
    EnergyRechargeCreate,
    EnergyRechargeOut,
    EnergyRechargePayIn,
)
from app.modules.client.services.energy.recharge_service import EnergyRechargeService

router = APIRouter()


class CancelIn(BaseModel):
    reason: str


@router.get("")
async def page_recharges(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    accountId: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyRechargeService.page(
        db, page, page_size, keyword, accountId, status,
    ))


@router.post("")
@operation_log(module="能源充值", action="新增", description="新增能源充值单")
async def create_recharge(
    data: EnergyRechargeCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    obj = await EnergyRechargeService.create(db, data, created_by=current_user.user_id)
    return success(data=EnergyRechargeOut.from_model(obj).model_dump())


@router.post("/{rid}/pay")
@operation_log(module="能源充值", action="入账", description="登记付款并入账")
async def pay_recharge(
    rid: int,
    data: EnergyRechargePayIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    obj = await EnergyRechargeService.register_pay(
        db, rid, data,
        operator_id=current_user.user_id,
        operator_name=getattr(current_user, "nickname", None),
    )
    return success(data=EnergyRechargeOut.from_model(obj).model_dump())


@router.post("/{rid}/cancel")
@operation_log(module="能源充值", action="撤销", description="撤销能源充值单")
async def cancel_recharge(
    rid: int,
    data: CancelIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    obj = await EnergyRechargeService.cancel(
        db, rid, data.reason,
        operator_id=current_user.user_id,
        operator_name=getattr(current_user, "nickname", None),
    )
    return success(data=EnergyRechargeOut.from_model(obj).model_dump())
