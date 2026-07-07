"""
承运运费引擎运维接口（计算任务 / 计算异常）
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.services.billing.carrier_freight_calc_task_service import (
    CarrierFreightCalcTaskService,
)
from app.modules.client.services.billing.carrier_freight_exception_service import (
    CarrierFreightExceptionService,
)

task_router = APIRouter()
exception_router = APIRouter()


# ============== 计算任务 ==============

@task_router.get("")
async def page_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    status: Optional[str] = None,
    taskType: Optional[str] = None,
    taskId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierFreightCalcTaskService.page_tasks(
        db, page=page, page_size=page_size,
        status=status, task_type=taskType, task_id=taskId,
    )
    return success(data=data)


@task_router.post("/{calc_task_id}/retry")
@operation_log(module="承运运费引擎", action="重试任务", description="重置承运运费计算任务为 pending")
async def retry_task(
    request: Request,
    calc_task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await CarrierFreightCalcTaskService.retry_task(db, calc_task_id)
    return success()


# ============== 计算异常 ==============

@exception_router.get("")
async def page_exceptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    status: Optional[str] = None,
    exceptionType: Optional[str] = None,
    taskId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierFreightExceptionService.page_exceptions(
        db, page=page, page_size=page_size,
        status=status, exception_type=exceptionType, task_id=taskId,
    )
    return success(data=data)


@exception_router.get("/stats")
async def stats_exceptions(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierFreightExceptionService.stats(db)
    return success(data=data)


class _ResolvePayload(BaseModel):
    remark: Optional[str] = None


@exception_router.post("/{exception_id}/resolve")
@operation_log(module="承运运费引擎", action="处理异常", description="标记承运运费异常为已处理")
async def resolve_exception(
    request: Request,
    exception_id: int,
    payload: _ResolvePayload = Body(default_factory=_ResolvePayload),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await CarrierFreightExceptionService.resolve(
        db, exception_id, user_id=current_user.user_id, remark=payload.remark,
    )
    return success()


@exception_router.post("/{exception_id}/ignore")
@operation_log(module="承运运费引擎", action="忽略异常", description="标记承运运费异常为已忽略")
async def ignore_exception(
    request: Request,
    exception_id: int,
    payload: _ResolvePayload = Body(default_factory=_ResolvePayload),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await CarrierFreightExceptionService.ignore(
        db, exception_id, user_id=current_user.user_id, remark=payload.remark,
    )
    return success()


class _BatchRecalcPayload(BaseModel):
    exceptionIds: list[int]


@exception_router.post("/batch-recalc")
@operation_log(module="承运运费引擎", action="批量重算异常", description="批量对异常关联任务重算")
async def batch_recalc_exceptions(
    request: Request,
    payload: _BatchRecalcPayload,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    data = await CarrierFreightExceptionService.batch_recalc(
        db, payload.exceptionIds, user_id=current_user.user_id,
    )
    return success(data=data)
