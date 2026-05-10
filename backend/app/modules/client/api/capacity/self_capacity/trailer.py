"""
自有运力-挂车管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.capacity.self_capacity.trailer import (
    TrailerCreate, TrailerUpdate,
)
from app.modules.client.services.capacity.self_capacity.trailer_service import (
    TrailerService,
)

router = APIRouter()


@router.get("")
async def page_trailers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    trailerType: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TrailerService.page_trailers(
        db, page=page, page_size=page_size,
        keyword=keyword, trailer_type=trailerType, status=status,
    )
    return success(data=data)


@router.get("/available")
async def list_available_trailers(
    excludeVehicleId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TrailerService.list_available_trailers(db, excludeVehicleId)
    return success(data=data)


@router.get("/{trailer_id}")
async def get_trailer(
    trailer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await TrailerService.get_trailer(db, trailer_id)
    return success(data=data.model_dump())


@router.post("")
@operation_log(module="挂车管理", action="新增", description="新增挂车")
async def create_trailer(
    request: Request,
    data: TrailerCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    trailer = await TrailerService.create_trailer(db, data)
    return success(data=trailer.model_dump())


@router.put("/{trailer_id}")
@operation_log(module="挂车管理", action="编辑", description="编辑挂车")
async def update_trailer(
    request: Request,
    trailer_id: int,
    data: TrailerUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    trailer = await TrailerService.update_trailer(db, trailer_id, data)
    return success(data=trailer.model_dump())


@router.delete("/{trailer_id}")
@operation_log(module="挂车管理", action="删除", description="删除挂车")
async def delete_trailer(
    request: Request,
    trailer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await TrailerService.delete_trailer(db, trailer_id)
    return success()
