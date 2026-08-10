"""
驾驶员任务接口（薄层包装 client/services/task/*）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.driver.schemas.task import (
    DriverAcceptTaskRequest,
    DriverConfirmArriveRequest,
    DriverConfirmLoadRequest,
    DriverDepartRequest,
    DriverRejectTaskRequest,
    DriverRevertSignRequest,
    DriverSignItemRequest,
)
from app.modules.driver.services.driver_context import get_current_driver
from app.modules.driver.services.driver_task_service import DriverTaskService

router = APIRouter()


@router.get("/my", summary="我的任务分页")
async def list_my_tasks(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=15, ge=1, le=100, alias="pageSize"),
    status: Optional[int] = Query(default=None, description="任务状态"),
    keyword: Optional[str] = Query(default=None, description="关键字（任务号 / 车牌 / 起讫点）"),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    items, total = await DriverTaskService.list_my_tasks(
        tenant_db, ctx,
        status=status,
        keyword=keyword,
        page=page,
        page_size=pageSize,
    )
    return success(
        data={
            "list": [it.model_dump() for it in items],
            "total": total,
            "page": page,
            "pageSize": pageSize,
        }
    )


@router.get("/{task_id}", summary="任务详情")
async def get_task_detail(
    task_id: int,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    detail = await DriverTaskService.get_my_task(tenant_db, ctx, task_id)
    return success(data=detail.model_dump())


@router.post("/{task_id}/accept", summary="接收调令")
async def accept_task(
    task_id: int,
    payload: DriverAcceptTaskRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    detail = await DriverTaskService.accept(tenant_db, ctx, task_id, payload)
    return success(data=detail.model_dump(), message="已接收调令")


@router.post("/{task_id}/reject", summary="拒绝调令")
async def reject_task(
    task_id: int,
    payload: DriverRejectTaskRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    await DriverTaskService.reject(tenant_db, ctx, task_id, payload)
    return success(message="已拒单，任务已退回待派车")


@router.post("/{task_id}/confirm-load", summary="确认装车")
async def confirm_load(
    task_id: int,
    payload: DriverConfirmLoadRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    detail = await DriverTaskService.confirm_load(tenant_db, ctx, task_id, payload)
    return success(data=detail.model_dump(), message="装车确认成功")


@router.post("/{task_id}/depart", summary="确认出发")
async def depart(
    task_id: int,
    payload: DriverDepartRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    detail = await DriverTaskService.depart(tenant_db, ctx, task_id, payload)
    return success(data=detail.model_dump(), message="出发成功")


@router.post("/{task_id}/confirm-arrive", summary="确认到达")
async def confirm_arrive(
    task_id: int,
    payload: DriverConfirmArriveRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    detail = await DriverTaskService.confirm_arrive(tenant_db, ctx, task_id, payload)
    return success(data=detail.model_dump(), message="到达确认成功")


@router.post("/items/{item_id}/sign", summary="挂接行交车")
async def sign_item(
    item_id: int,
    payload: DriverSignItemRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    await DriverTaskService.sign_item(tenant_db, ctx, item_id, payload)
    return success(message="交车成功")


@router.post("/items/{item_id}/revert-sign", summary="撤销交车（受限）")
async def revert_sign_item(
    item_id: int,
    payload: DriverRevertSignRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    await DriverTaskService.revert_sign_item(
        tenant_db, ctx, item_id, payload, actor=current_user
    )
    return success(message="已撤销交车")
