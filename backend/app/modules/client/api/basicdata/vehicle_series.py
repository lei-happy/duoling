"""
企业端车系 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.basicdata.vehicle_series import (
    VehicleSeriesCreate,
    VehicleSeriesUpdate,
    VehicleSeriesOut,
)
from app.modules.client.services.basicdata.tenant_vehicle_series_service import (
    TenantVehicleSeriesService,
)

router = APIRouter()


@router.get("")
async def page_series(
    brandId: int = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TenantVehicleSeriesService.page_series(
        db,
        brand_id=brandId,
        page=page,
        limit=limit,
        keyword=keyword,
    )
    return success(data=data)


@router.get("/{series_id}")
async def get_series(
    series_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    item = await TenantVehicleSeriesService.get_series(db, series_id)
    return success(data=item.model_dump())


@router.post("")
@operation_log(module="品牌车型", action="新增", description="新增车系")
async def create_series(
    request: Request,
    data: VehicleSeriesCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    row = await TenantVehicleSeriesService.create_series(db, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleSeriesOut.from_model(row).model_dump()
    return success(data=payload)


@router.put("/{series_id}")
@operation_log(module="品牌车型", action="编辑", description="编辑车系")
async def update_series(
    request: Request,
    series_id: int,
    data: VehicleSeriesUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    row = await TenantVehicleSeriesService.update_series(db, series_id, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleSeriesOut.from_model(row).model_dump()
    return success(data=payload)


@router.delete("/{series_id}")
@operation_log(module="品牌车型", action="删除", description="删除车系")
async def delete_series(
    request: Request,
    series_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await TenantVehicleSeriesService.delete_series(db, series_id)
    return success()
