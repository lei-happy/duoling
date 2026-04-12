"""
企业端驾驶员账户管理 API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.driver import (
    DriverAccountCreate, DriverAccountUpdate,
)
from app.modules.client.services.driver import DriverAccountService

router = APIRouter()


@router.get("/{driver_id}/accounts")
async def list_accounts(
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverAccountService.list_accounts(db, driver_id)
    return success(data=data)


@router.post("/{driver_id}/accounts")
@operation_log(module="驾驶员管理", action="新增账户", description="新增驾驶员账户")
async def create_account(
    request: Request,
    driver_id: int,
    data: DriverAccountCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    account = await DriverAccountService.create_account(db, driver_id, data)
    return success(data=account.model_dump())


@router.put("/accounts/{account_id}")
@operation_log(module="驾驶员管理", action="编辑账户", description="编辑驾驶员账户")
async def update_account(
    request: Request,
    account_id: int,
    data: DriverAccountUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    account = await DriverAccountService.update_account(db, account_id, data)
    return success(data=account.model_dump())


@router.put("/accounts/{account_id}/status")
@operation_log(module="驾驶员管理", action="账户状态变更", description="修改驾驶员账户状态")
async def toggle_account_status(
    request: Request,
    account_id: int,
    data: dict,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    account = await DriverAccountService.toggle_status(
        db, account_id, data.get("status", 0)
    )
    return success(data=account.model_dump())


@router.delete("/accounts/{account_id}")
@operation_log(module="驾驶员管理", action="删除账户", description="删除驾驶员账户")
async def delete_account(
    request: Request,
    account_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await DriverAccountService.delete_account(db, account_id)
    return success()
