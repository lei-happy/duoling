from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, OrderOut,
)
from app.modules.client.services.order_service import OrderService

router = APIRouter()


@router.get("")
async def page_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await OrderService.page_orders(
        db, page=page, page_size=page_size,
        keyword=keyword, status=status,
    )
    return success(data=data)


@router.get("/dispatch")
async def page_dispatch_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await OrderService.page_orders(
        db, page=page, page_size=page_size,
        keyword=keyword, status_in=[0, 1],
    )
    return success(data=data)


@router.get("/tracking")
async def page_tracking_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await OrderService.page_orders(
        db, page=page, page_size=page_size,
        keyword=keyword, status_in=[2],
    )
    return success(data=data)


@router.get("/receipt")
async def page_receipt_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await OrderService.page_orders(
        db, page=page, page_size=page_size,
        keyword=keyword, status_in=[3, 4],
    )
    return success(data=data)


@router.post("")
@operation_log(module="运单管理", action="新增", description="新增运单")
async def create_order(
    request: Request,
    data: OrderCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    order = await OrderService.create_order(db, data)
    return success(data=OrderOut.from_model(order).model_dump())


@router.put("/{order_id}")
@operation_log(module="运单管理", action="编辑", description="编辑运单")
async def update_order(
    request: Request,
    order_id: int,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    order = await OrderService.update_order(db, order_id, data)
    return success(data=OrderOut.from_model(order).model_dump())


@router.put("/{order_id}/status")
@operation_log(module="运单管理", action="状态变更", description="变更运单状态")
async def update_order_status(
    request: Request,
    order_id: int,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    order = await OrderService.update_order_status(db, order_id, data)
    return success(data=OrderOut.from_model(order).model_dump())


@router.delete("/{order_id}")
@operation_log(module="运单管理", action="删除", description="删除运单")
async def delete_order(
    request: Request,
    order_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await OrderService.delete_order(db, order_id)
    return success()
