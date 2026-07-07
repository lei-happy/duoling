"""
企业端承运商合同 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.core.security import TokenData
from app.modules.client.schemas.billing.carrier_contract import (
    CarrierContractCreate, CarrierContractUpdate, CarrierContractOut,
)
from app.modules.client.schemas.billing.carrier_rate import (
    CarrierRateCreate, CarrierRateOut,
)
from app.modules.client.services.billing.carrier_contract_service import (
    CarrierContractService,
)
from app.modules.client.services.billing.carrier_rate_service import CarrierRateService

router = APIRouter()


@router.get("")
async def page_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    carrierId: Optional[int] = None,
    status: Optional[int] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierContractService.page_contracts(
        db, page=page, page_size=page_size, keyword=keyword,
        carrier_id=carrierId, status=status, sort=sort, order=order,
    )
    return success(data=data)


@router.get("/{contract_id}")
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await CarrierContractService.get_contract(db, contract_id)
    return success(data=CarrierContractOut.from_model(contract).model_dump())


@router.post("")
@operation_log(module="承运商合同", action="新增", description="新增承运商合同")
async def create_contract(
    request: Request,
    data: CarrierContractCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await CarrierContractService.create_contract(db, data)
    return success(data=CarrierContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}")
@operation_log(module="承运商合同", action="编辑", description="编辑承运商合同")
async def update_contract(
    request: Request,
    contract_id: int,
    data: CarrierContractUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    contract = await CarrierContractService.update_contract(
        db, contract_id, data, current_user_id=current_user.user_id,
    )
    return success(data=CarrierContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}/activate")
@operation_log(module="承运商合同", action="激活", description="激活承运商合同")
async def activate_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    contract = await CarrierContractService.activate_contract(
        db, contract_id, current_user_id=current_user.user_id,
    )
    return success(data=CarrierContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}/terminate")
@operation_log(module="承运商合同", action="终止", description="终止承运商合同")
async def terminate_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    contract = await CarrierContractService.terminate_contract(
        db, contract_id, current_user_id=current_user.user_id,
    )
    return success(data=CarrierContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}/resume")
@operation_log(module="承运商合同", action="恢复生效", description="恢复已终止的承运商合同")
async def resume_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    contract = await CarrierContractService.resume_contract(
        db, contract_id, current_user_id=current_user.user_id,
    )
    return success(data=CarrierContractOut.from_model(contract).model_dump())


@router.delete("/{contract_id}")
@operation_log(module="承运商合同", action="删除", description="删除承运商合同")
async def delete_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await CarrierContractService.delete_contract(db, contract_id)
    return success()


@router.get("/{contract_id}/rate")
async def list_rates(
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CarrierRateService.list_by_contract(db, contract_id)
    return success(data=data)


@router.post("/{contract_id}/rate")
@operation_log(module="承运价规则", action="新增", description="新增承运价规则")
async def create_rate(
    request: Request,
    contract_id: int,
    data: CarrierRateCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    contract = await CarrierContractService.get_contract(db, contract_id)
    data.contractId = contract_id
    data.carrierId = contract.carrier_id
    rate = await CarrierRateService.create_rate(
        db, data, current_user_id=current_user.user_id,
    )
    return success(data=CarrierRateOut.from_model(rate).model_dump())
