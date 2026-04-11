"""
企业端运单管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.waybill.waybill import (
    WaybillCreate, WaybillUpdate, WaybillStatusUpdate, WaybillOut,
)
from app.modules.client.services.waybill.waybill_service import WaybillService

router = APIRouter()


@router.get("")
async def page_waybills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    status: Optional[int] = None,
    freightSource: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await WaybillService.page_waybills(
        db, page=page, page_size=page_size,
        keyword=keyword, customer_id=customerId,
        status=status, freight_source=freightSource,
    )
    return success(data=data)


@router.get("/{waybill_id}")
async def get_waybill(
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.get_waybill(db, waybill_id)
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.post("")
@operation_log(module="运单管理", action="新增", description="新增运单")
async def create_waybill(
    request: Request,
    data: WaybillCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user=Depends(get_current_user),
):
    waybill = await WaybillService.create_waybill(db, data, current_user.user_id)
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.put("/{waybill_id}")
@operation_log(module="运单管理", action="编辑", description="编辑运单")
async def update_waybill(
    request: Request,
    waybill_id: int,
    data: WaybillUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.update_waybill(db, waybill_id, data)
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.put("/{waybill_id}/status")
@operation_log(module="运单管理", action="状态变更", description="变更运单状态")
async def update_waybill_status(
    request: Request,
    waybill_id: int,
    data: WaybillStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.update_status(db, waybill_id, data)
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.delete("/{waybill_id}")
@operation_log(module="运单管理", action="删除", description="删除运单")
async def delete_waybill(
    request: Request,
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await WaybillService.delete_waybill(db, waybill_id)
    return success()
