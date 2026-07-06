"""
自有运力-驾驶员资金账户（往来账）API

区别于收款账户（/accounts）：本组接口维护司机与公司之间的资金往来台账，
余额只能通过流水改变，流水 append-only。
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.capacity.self_capacity.driver import (
    DriverFundAccountStatusUpdate,
    DriverFundTransactionCreate,
)
from app.modules.client.services.capacity.self_capacity.driver import (
    DriverFundAccountService,
)

router = APIRouter()


@router.get("/{driver_id}/fund-account")
async def get_fund_account(
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    data = await DriverFundAccountService.get_account(db, driver_id)
    return success(data=data.model_dump())


@router.get("/{driver_id}/fund-account/transactions")
async def list_fund_transactions(
    driver_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    bizType: Optional[int] = None,
    source: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    items, total = await DriverFundAccountService.list_transactions(
        db, driver_id,
        biz_type=bizType, source=source, start=start, end=end,
        page=page, page_size=page_size,
    )
    return success(data={"list": items, "total": total})


@router.post("/{driver_id}/fund-account/transactions")
@operation_log(module="驾驶员管理", action="资金账户记账", description="驾驶员资金账户记账")
async def post_fund_transaction(
    request: Request,
    driver_id: int,
    data: DriverFundTransactionCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    txn = await DriverFundAccountService.post_transaction(
        db, driver_id, data, operator_id=current_user.user_id
    )
    return success(data=txn.model_dump())


@router.patch("/fund-account/{account_id}/status")
@operation_log(module="驾驶员管理", action="资金账户状态", description="冻结/解冻驾驶员资金账户")
async def toggle_fund_account_status(
    request: Request,
    account_id: int,
    data: DriverFundAccountStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    acc = await DriverFundAccountService.toggle_status(db, account_id, data.status)
    return success(data=acc.model_dump())
