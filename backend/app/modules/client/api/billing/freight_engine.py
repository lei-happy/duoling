"""
计费引擎运维接口（任务 / 异常 / 别名）
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
from app.modules.client.services.billing.alias_service import (
    RegionAliasService,
    VehicleAliasService,
)
from app.modules.client.services.billing.freight_calc_task_service import (
    FreightCalcTaskService,
)
from app.modules.client.services.billing.freight_exception_service import (
    FreightExceptionService,
)


# 三套接口共享前缀通过 client/api/__init__.py 挂载，因此本文件只定义路由本身
task_router = APIRouter()
exception_router = APIRouter()
region_alias_router = APIRouter()
vehicle_alias_router = APIRouter()


# ============== 任务 ==============

@task_router.get("")
async def page_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    status: Optional[str] = None,
    taskType: Optional[str] = None,
    waybillId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await FreightCalcTaskService.page_tasks(
        db, page=page, page_size=page_size,
        status=status, task_type=taskType, waybill_id=waybillId,
    )
    return success(data=data)


@task_router.post("/{task_id}/retry")
@operation_log(module="计费引擎", action="重试任务", description="重置任务为 pending")
async def retry_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await FreightCalcTaskService.retry_task(db, task_id)
    return success()


# ============== 异常 ==============

@exception_router.get("")
async def page_exceptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    status: Optional[str] = None,
    exceptionType: Optional[str] = None,
    waybillId: Optional[int] = None,
    batchId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await FreightExceptionService.page_exceptions(
        db, page=page, page_size=page_size,
        status=status, exception_type=exceptionType,
        waybill_id=waybillId, batch_id=batchId,
    )
    return success(data=data)


@exception_router.get("/stats")
async def stats_exceptions(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await FreightExceptionService.stats(db)
    return success(data=data)


class _ResolvePayload(BaseModel):
    remark: Optional[str] = None


@exception_router.post("/{exception_id}/resolve")
@operation_log(module="计费引擎", action="处理异常", description="标记异常为已处理")
async def resolve_exception(
    request: Request,
    exception_id: int,
    payload: _ResolvePayload = Body(default_factory=_ResolvePayload),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await FreightExceptionService.resolve(
        db, exception_id, user_id=current_user.user_id,
        remark=payload.remark,
    )
    return success()


@exception_router.post("/{exception_id}/ignore")
@operation_log(module="计费引擎", action="忽略异常", description="标记异常为已忽略")
async def ignore_exception(
    request: Request,
    exception_id: int,
    payload: _ResolvePayload = Body(default_factory=_ResolvePayload),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await FreightExceptionService.ignore(
        db, exception_id, user_id=current_user.user_id,
        remark=payload.remark,
    )
    return success()


class _BatchRecalcPayload(BaseModel):
    exceptionIds: list[int]


@exception_router.post("/batch-recalc")
@operation_log(module="计费引擎", action="批量重算异常", description="批量对异常关联计划重算")
async def batch_recalc_exceptions(
    request: Request,
    payload: _BatchRecalcPayload,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    data = await FreightExceptionService.batch_recalc(
        db, payload.exceptionIds, user_id=current_user.user_id,
    )
    return success(data=data)


# ============== 地名别名 ==============

class _RegionAliasIn(BaseModel):
    aliasName: str
    regionId: int


@region_alias_router.get("")
async def page_region_alias(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await RegionAliasService.page(
        db, page=page, page_size=page_size, keyword=keyword,
    )
    return success(data=data)


@region_alias_router.post("")
@operation_log(module="基础数据", action="新增地名别名", description="维护地名别名")
async def upsert_region_alias(
    request: Request,
    payload: _RegionAliasIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    m = await RegionAliasService.upsert(db, payload.aliasName, payload.regionId)
    return success(data={"id": m.id})


@region_alias_router.delete("/{alias_id}")
@operation_log(module="基础数据", action="删除地名别名", description="删除地名别名")
async def delete_region_alias(
    request: Request,
    alias_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await RegionAliasService.delete(db, alias_id)
    return success()


# ============== 车型 / 品牌别名 ==============

class _VehicleAliasIn(BaseModel):
    aliasKind: str  # brand / series
    rawBrand: Optional[str] = None
    rawModel: Optional[str] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None


@vehicle_alias_router.get("")
async def page_vehicle_alias(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    kind: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await VehicleAliasService.page(
        db, page=page, page_size=page_size, keyword=keyword, kind=kind,
    )
    return success(data=data)


@vehicle_alias_router.post("")
@operation_log(module="基础数据", action="新增车型别名", description="维护车型/品牌别名")
async def upsert_vehicle_alias(
    request: Request,
    payload: _VehicleAliasIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    m = await VehicleAliasService.upsert(
        db,
        alias_kind=payload.aliasKind,
        raw_brand=payload.rawBrand, raw_model=payload.rawModel,
        brand_id=payload.brandId, series_id=payload.seriesId,
    )
    return success(data={"id": m.id})


@vehicle_alias_router.delete("/{alias_id}")
@operation_log(module="基础数据", action="删除车型别名", description="删除车型/品牌别名")
async def delete_vehicle_alias(
    request: Request,
    alias_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await VehicleAliasService.delete(db, alias_id)
    return success()


# ============== 双引擎回归对比（Phase 8） ==============

regression_router = APIRouter()


class _RegressionRequest(BaseModel):
    customerId: Optional[int] = None
    dateFrom: Optional[str] = None  # YYYY-MM-DD
    dateTo: Optional[str] = None
    onlyCalculated: bool = True
    limit: int = 200
    minorThreshold: float = 1.0


@regression_router.post("/run")
async def run_regression(
    payload: _RegressionRequest = Body(...),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """运行双引擎对比报表（dry_run，不写库）"""
    from datetime import date as _date
    from decimal import Decimal as _D
    from app.modules.client.services.billing.dual_engine_compare_service import (
        DualEngineCompareService,
    )

    def _parse(d):
        if not d:
            return None
        try:
            return _date.fromisoformat(d)
        except ValueError:
            return None

    report = await DualEngineCompareService.compare_batch(
        db,
        customer_id=payload.customerId,
        date_from=_parse(payload.dateFrom),
        date_to=_parse(payload.dateTo),
        only_calculated=payload.onlyCalculated,
        limit=max(1, min(payload.limit, 1000)),
        minor_threshold=_D(str(payload.minorThreshold)),
    )
    return success(data=DualEngineCompareService.report_to_dict(report))
