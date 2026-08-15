from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.schemas.energy.supplier import (
    EnergyStationCreate,
    EnergyStationUpdate,
    EnergySupplierCreate,
    EnergySupplierOut,
    EnergySupplierUpdate,
)
from app.modules.client.services.energy.supplier_service import (
    EnergyStationService,
    EnergySupplierService,
)

supplier_router = APIRouter()
station_router = APIRouter()


@supplier_router.get("")
async def page_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    supplierType: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergySupplierService.page(
        db, page, page_size, keyword, supplierType, status,
    ))


@supplier_router.post("")
@operation_log(module="能源供应商", action="新增", description="新增能源供应商")
async def create_supplier(
    data: EnergySupplierCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergySupplierService.create(db, data)
    return success(data=EnergySupplierOut.from_model(obj).model_dump())


@supplier_router.put("/{sid}")
@operation_log(module="能源供应商", action="编辑", description="编辑能源供应商")
async def update_supplier(
    sid: int,
    data: EnergySupplierUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergySupplierService.update(db, sid, data)
    return success(data=EnergySupplierOut.from_model(obj).model_dump())


@supplier_router.delete("/{sid}")
@operation_log(module="能源供应商", action="删除", description="删除能源供应商")
async def delete_supplier(
    sid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergySupplierService.delete(db, sid)
    return success()


@station_router.get("")
async def page_stations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    supplierId: Optional[int] = None,
    keyword: Optional[str] = None,
    energyType: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyStationService.page(
        db, page, page_size, supplierId, keyword, energyType,
    ))


@station_router.get("/{sid}")
async def get_station(
    sid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyStationService.detail(db, sid))


@station_router.post("")
@operation_log(module="能源站点", action="新增", description="新增能源站点")
async def create_station(
    data: EnergyStationCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyStationService.create(db, data)
    return success(data=await EnergyStationService.detail(db, obj.id))


@station_router.put("/{sid}")
@operation_log(module="能源站点", action="编辑", description="编辑能源站点")
async def update_station(
    sid: int,
    data: EnergyStationUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyStationService.update(db, sid, data)
    return success(data=await EnergyStationService.detail(db, obj.id))


@station_router.delete("/{sid}")
@operation_log(module="能源站点", action="删除", description="删除能源站点")
async def delete_station(
    sid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyStationService.delete(db, sid)
    return success()
