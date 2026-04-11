"""
企业端经销商 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.basicdata.dealer import (
    DealerCreate,
    DealerUpdate,
    DealerOut,
)
from app.modules.client.services.basicdata.tenant_dealer_service import (
    TenantDealerService,
)

router = APIRouter()


@router.get("")
async def page_dealers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    sort: Optional[str] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TenantDealerService.page_dealers(
        db,
        page=page,
        limit=limit,
        keyword=keyword,
        sort=sort,
        order=order,
    )
    return success(data=data)


@router.get("/{dealer_id}")
async def get_dealer(
    dealer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    item = await TenantDealerService.get_dealer(db, dealer_id)
    return success(data=item.model_dump())


@router.post("")
@operation_log(module="经销商门店", action="新增", description="新增经销商")
async def create_dealer(
    request: Request,
    data: DealerCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    row = await TenantDealerService.create_dealer(db, data)
    await db.flush()
    await db.refresh(row)
    payload = DealerOut.from_model(row).model_dump()
    return success(data=payload)


@router.put("/{dealer_id}")
@operation_log(module="经销商门店", action="编辑", description="编辑经销商")
async def update_dealer(
    request: Request,
    dealer_id: int,
    data: DealerUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    row = await TenantDealerService.update_dealer(db, dealer_id, data)
    await db.flush()
    await db.refresh(row)
    payload = DealerOut.from_model(row).model_dump()
    return success(data=payload)


@router.delete("/{dealer_id}")
@operation_log(module="经销商门店", action="删除", description="删除经销商")
async def delete_dealer(
    request: Request,
    dealer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await TenantDealerService.delete_dealer(db, dealer_id)
    return success()
