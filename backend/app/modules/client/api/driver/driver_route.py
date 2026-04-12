"""
企业端驾驶员常跑线路 API
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.driver.driver_route import DriverRouteCreate
from app.modules.client.services.driver.driver_route_service import DriverRouteService

router = APIRouter()


@router.get("/{driver_id}/routes")
async def list_routes(
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverRouteService.list_routes(db, driver_id)
    return success(data=data)


@router.put("/{driver_id}/routes")
@operation_log(module="驾驶员管理", action="保存线路", description="保存驾驶员常跑线路")
async def save_routes(
    request: Request,
    driver_id: int,
    routes: List[DriverRouteCreate],
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverRouteService.save_routes(db, driver_id, routes)
    return success(data=data)
