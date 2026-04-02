"""
企业端路线管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.route import (
    RouteCreate, RouteUpdate, RouteOut,
)
from app.modules.client.services.route_service import RouteService

router = APIRouter()


@router.get("")
async def page_routes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await RouteService.page_routes(
        db, page=page, page_size=page_size,
        keyword=keyword, status=status,
    )
    return success(data=data)


@router.get("/list")
async def list_routes(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    items = await RouteService.list_routes(db)
    return success(data=[RouteOut.from_model(r).model_dump() for r in items])


@router.post("")
@operation_log(module="路线管理", action="新增", description="新增路线")
async def create_route(
    request: Request,
    data: RouteCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    route = await RouteService.create_route(db, data)
    return success(data=RouteOut.from_model(route).model_dump())


@router.put("/{route_id}")
@operation_log(module="路线管理", action="编辑", description="编辑路线")
async def update_route(
    request: Request,
    route_id: int,
    data: RouteUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    route = await RouteService.update_route(db, route_id, data)
    return success(data=RouteOut.from_model(route).model_dump())


@router.delete("/{route_id}")
@operation_log(module="路线管理", action="删除", description="删除路线")
async def delete_route(
    request: Request,
    route_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await RouteService.delete_route(db, route_id)
    return success()
