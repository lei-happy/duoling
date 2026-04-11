"""
Console 平台车系 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.basicdata.vehicle_series import (
    VehicleSeriesCreate,
    VehicleSeriesUpdate,
    VehicleSeriesOut,
)
from app.modules.console.services.basicdata.vehicle_series_service import (
    VehicleSeriesService,
)

router = APIRouter()


@router.get("")
async def page_series(
    brandId: int = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await VehicleSeriesService.page_series(
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
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    item = await VehicleSeriesService.get_series(db, series_id)
    return success(data=item.model_dump())


@router.post("")
async def create_series(
    data: VehicleSeriesCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await VehicleSeriesService.create_series(db, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleSeriesOut.from_model(row).model_dump()
    return success(data=payload)


@router.put("/{series_id}")
async def update_series(
    series_id: int,
    data: VehicleSeriesUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await VehicleSeriesService.update_series(db, series_id, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleSeriesOut.from_model(row).model_dump()
    return success(data=payload)


@router.delete("/{series_id}")
async def delete_series(
    series_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await VehicleSeriesService.delete_series(db, series_id)
    return success()
