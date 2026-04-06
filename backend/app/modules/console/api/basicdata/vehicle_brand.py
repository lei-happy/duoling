"""
Console 平台品牌 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.basicdata.vehicle_brand import (
    VehicleBrandCreate,
    VehicleBrandUpdate,
    VehicleBrandOut,
)
from app.modules.console.services.basicdata.vehicle_brand_service import (
    VehicleBrandService,
)

router = APIRouter()


@router.get("")
async def page_brands(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await VehicleBrandService.page_brands(
        db, page=page, limit=limit, keyword=keyword
    )
    return success(data=data)


@router.get("/options")
async def list_brand_options(
    keyword: Optional[str] = Query(None),
    limit: int = Query(2000, ge=1, le=5000),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await VehicleBrandService.list_brand_options(
        db, keyword=keyword, limit=limit
    )
    return success(data=data)


@router.get("/{brand_id}")
async def get_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    item = await VehicleBrandService.get_brand(db, brand_id)
    return success(data=item.model_dump())


@router.post("")
async def create_brand(
    data: VehicleBrandCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await VehicleBrandService.create_brand(db, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleBrandOut.from_model(row).model_dump()
    await db.commit()
    return success(data=payload)


@router.put("/{brand_id}")
async def update_brand(
    brand_id: int,
    data: VehicleBrandUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await VehicleBrandService.update_brand(db, brand_id, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleBrandOut.from_model(row).model_dump()
    await db.commit()
    return success(data=payload)


@router.delete("/{brand_id}")
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await VehicleBrandService.delete_brand(db, brand_id)
    await db.commit()
    return success()
