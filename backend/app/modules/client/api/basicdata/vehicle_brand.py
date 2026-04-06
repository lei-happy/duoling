"""
企业端品牌 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.basicdata.vehicle_brand import (
    VehicleBrandCreate,
    VehicleBrandUpdate,
    VehicleBrandOut,
)
from app.modules.client.services.basicdata.tenant_vehicle_brand_service import (
    TenantVehicleBrandService,
)

router = APIRouter()


@router.get("")
async def page_brands(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TenantVehicleBrandService.page_brands(
        db, page=page, limit=limit, keyword=keyword
    )
    return success(data=data)


@router.get("/options")
async def list_brand_options(
    keyword: Optional[str] = Query(None),
    limit: int = Query(2000, ge=1, le=5000),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TenantVehicleBrandService.list_brand_options(
        db, keyword=keyword, limit=limit
    )
    return success(data=data)


@router.get("/{brand_id}")
async def get_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    item = await TenantVehicleBrandService.get_brand(db, brand_id)
    return success(data=item.model_dump())


@router.post("")
@operation_log(module="品牌车型", action="新增", description="新增品牌")
async def create_brand(
    request: Request,
    data: VehicleBrandCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    row = await TenantVehicleBrandService.create_brand(db, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleBrandOut.from_model(row).model_dump()
    return success(data=payload)


@router.put("/{brand_id}")
@operation_log(module="品牌车型", action="编辑", description="编辑品牌")
async def update_brand(
    request: Request,
    brand_id: int,
    data: VehicleBrandUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    row = await TenantVehicleBrandService.update_brand(db, brand_id, data)
    await db.flush()
    await db.refresh(row)
    payload = VehicleBrandOut.from_model(row).model_dump()
    return success(data=payload)


@router.delete("/{brand_id}")
@operation_log(module="品牌车型", action="删除", description="删除品牌")
async def delete_brand(
    request: Request,
    brand_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await TenantVehicleBrandService.delete_brand(db, brand_id)
    return success()
