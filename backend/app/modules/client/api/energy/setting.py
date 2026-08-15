from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.services.energy.setting_service import (
    EnergyProductService,
    EnergyRuleService,
    EnergyVehicleProfileService,
)

product_router = APIRouter()
profile_router = APIRouter()
rule_router = APIRouter()


class ProductIn(BaseModel):
    energyType: str = "OIL"
    productCode: Optional[str] = None
    productName: str
    standardUnit: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class ProfileIn(BaseModel):
    vehicleId: int
    energyType: str = "OIL"
    defaultProductId: Optional[int] = None
    tankCapacity: Optional[float] = None
    batteryCapacity: Optional[float] = None
    standardConsumptionPer100km: Optional[float] = None
    remark: Optional[str] = None


class RuleIn(BaseModel):
    thresholdValue: Optional[float] = None
    riskLevel: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


@product_router.get("")
async def list_products(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyProductService.list_all(db))


@product_router.post("")
@operation_log(module="能源商品", action="新增", description="新增能源商品")
async def create_product(
    data: ProductIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyProductService.create(db, data.model_dump())
    return success(data={"id": obj.id})


@product_router.put("/{pid}")
@operation_log(module="能源商品", action="编辑", description="编辑能源商品")
async def update_product(
    pid: int,
    data: ProductIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyProductService.update(db, pid, data.model_dump(exclude_unset=True))
    return success()


@product_router.delete("/{pid}")
@operation_log(module="能源商品", action="删除", description="删除能源商品")
async def delete_product(
    pid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyProductService.delete(db, pid)
    return success()


@profile_router.get("")
async def page_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyVehicleProfileService.page(db, page, page_size))


@profile_router.post("")
@operation_log(module="车辆能源档案", action="保存", description="保存车辆能源档案")
async def upsert_profile(
    data: ProfileIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyVehicleProfileService.upsert(db, data.model_dump())
    return success(data={"id": obj.id})


@rule_router.get("")
async def list_rules(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyRuleService.list_all(db))


@rule_router.put("/{rid}")
@operation_log(module="能源风控", action="编辑", description="编辑风控规则")
async def update_rule(
    rid: int,
    data: RuleIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyRuleService.update(db, rid, data.model_dump(exclude_unset=True))
    return success()
