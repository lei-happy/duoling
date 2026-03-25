"""
企业端驾驶员管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.driver import (
    DriverCreate, DriverUpdate, DriverOut,
)
from app.modules.client.services.driver_service import DriverService

router = APIRouter()


@router.get("")
async def page_drivers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    licenseType: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverService.page_drivers(
        db, page=page, page_size=page_size,
        keyword=keyword, license_type=licenseType, status=status,
    )
    return success(data=data)


@router.post("")
async def create_driver(
    data: DriverCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    driver = await DriverService.create_driver(db, data)
    return success(data=DriverOut.from_model(driver).model_dump())


@router.put("/{driver_id}")
async def update_driver(
    driver_id: int,
    data: DriverUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    driver = await DriverService.update_driver(db, driver_id, data)
    return success(data=DriverOut.from_model(driver).model_dump())


@router.delete("/{driver_id}")
async def delete_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await DriverService.delete_driver(db, driver_id)
    return success()
