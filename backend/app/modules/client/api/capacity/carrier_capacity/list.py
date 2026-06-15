"""
承运商运力 - 建档 API

挂在某承运商（biz_carrier）名下的车 + 人 + 证照档案，支持 CRUD 与状态变更，
证照到期由独立的证照监控引擎统一扫描。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user, get_tenant_code
from app.core.database import db_manager
from app.core.security import TokenData
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.capacity.carrier_capacity.carrier_capacity import (
    CarrierCapacityCreate,
    CarrierCapacityStatusUpdate,
    CarrierCapacityUpdate,
)
from app.modules.client.services.capacity.carrier_capacity.carrier_capacity_service import (
    CarrierCapacityService,
)

_CC_TABLES = [
    "biz_carrier_capacity",
    "biz_carrier_capacity_vehicle",
    "biz_carrier_capacity_driver",
]


async def _ensure_cc_tables(tenant_code: str = Depends(get_tenant_code)) -> None:
    """老租户库幂等补建承运商运力相关表。"""
    await db_manager.ensure_tenant_tables(tenant_code, _CC_TABLES)


router = APIRouter(dependencies=[Depends(_ensure_cc_tables)])


@router.get("")
async def page_carrier_capacities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    carrierId: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierCapacityService.page(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        carrier_id=carrierId,
        status=status,
    )
    return success(data=data)


@router.get("/{cc_id}")
async def get_carrier_capacity(
    cc_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierCapacityService.get_detail(db, cc_id)
    return success(data=data.model_dump())


@router.post("")
@operation_log(module="承运商运力", action="新增", description="新增承运商运力")
async def create_carrier_capacity(
    request: Request,
    data: CarrierCapacityCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    detail = await CarrierCapacityService.create(db, data, current_user.user_id)
    return success(data=detail.model_dump())


@router.put("/{cc_id}")
@operation_log(module="承运商运力", action="编辑", description="编辑承运商运力")
async def update_carrier_capacity(
    request: Request,
    cc_id: int,
    data: CarrierCapacityUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    detail = await CarrierCapacityService.update(db, cc_id, data, current_user.user_id)
    return success(data=detail.model_dump())


@router.put("/{cc_id}/status")
@operation_log(module="承运商运力", action="状态变更", description="变更承运商运力状态")
async def change_carrier_capacity_status(
    request: Request,
    cc_id: int,
    data: CarrierCapacityStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await CarrierCapacityService.update_status(db, cc_id, data.status, data.statusRemark)
    return success()


@router.delete("/{cc_id}")
@operation_log(module="承运商运力", action="删除", description="删除承运商运力")
async def delete_carrier_capacity(
    request: Request,
    cc_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await CarrierCapacityService.delete(db, cc_id)
    return success()
