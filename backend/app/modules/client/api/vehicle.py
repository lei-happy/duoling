"""
企业端车辆管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleStatusUpdate,
)
from app.modules.client.services.vehicle_service import VehicleService
from app.modules.client.services.vehicle_status_service import VehicleStatusService

router = APIRouter()


@router.get("")
async def page_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    vehicleType: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await VehicleService.page_vehicles(
        db, page=page, page_size=page_size,
        keyword=keyword, vehicle_type=vehicleType, status=status,
    )
    return success(data=data)


@router.get("/{vehicle_id}")
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await VehicleService.get_vehicle(db, vehicle_id)
    return success(data=data.model_dump())


@router.post("")
async def create_vehicle(
    data: VehicleCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    vehicle = await VehicleService.create_vehicle(db, data)
    return success(data=vehicle.model_dump())


@router.put("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    vehicle = await VehicleService.update_vehicle(db, vehicle_id, data)
    return success(data=vehicle.model_dump())


@router.put("/{vehicle_id}/status")
async def change_vehicle_status(
    vehicle_id: int,
    data: VehicleStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await VehicleStatusService.change_status(
        db, vehicle_id, data.status, data.statusSource
    )
    return success()


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await VehicleService.delete_vehicle(db, vehicle_id)
    return success()
