"""
企业端运价合同 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.billing.freight_contract import (
    FreightContractCreate, FreightContractUpdate, FreightContractOut,
)
from app.modules.client.schemas.billing.freight_rate import (
    FreightRateCreate, FreightRateOut,
)
from app.modules.client.services.billing.freight_contract_service import FreightContractService
from app.modules.client.services.billing.freight_rate_service import FreightRateService

router = APIRouter()


@router.get("")
async def page_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    status: Optional[int] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await FreightContractService.page_contracts(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        customer_id=customerId,
        status=status,
        sort=sort,
        order=order,
    )
    return success(data=data)


@router.get("/{contract_id}")
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.get_contract(db, contract_id)
    return success(data=FreightContractOut.from_model(contract).model_dump())


@router.post("")
@operation_log(module="运价合同", action="新增", description="新增运价合同")
async def create_contract(
    request: Request,
    data: FreightContractCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.create_contract(db, data)
    return success(data=FreightContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}")
@operation_log(module="运价合同", action="编辑", description="编辑运价合同")
async def update_contract(
    request: Request,
    contract_id: int,
    data: FreightContractUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.update_contract(db, contract_id, data)
    return success(data=FreightContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}/activate")
@operation_log(module="运价合同", action="激活", description="激活运价合同")
async def activate_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.activate_contract(db, contract_id)
    return success(data=FreightContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}/terminate")
@operation_log(module="运价合同", action="终止", description="终止运价合同")
async def terminate_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.terminate_contract(db, contract_id)
    return success(data=FreightContractOut.from_model(contract).model_dump())


@router.put("/{contract_id}/resume")
@operation_log(module="运价合同", action="恢复生效", description="恢复已终止的运价合同")
async def resume_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.resume_contract(db, contract_id)
    return success(data=FreightContractOut.from_model(contract).model_dump())


@router.delete("/{contract_id}")
@operation_log(module="运价合同", action="删除", description="删除运价合同")
async def delete_contract(
    request: Request,
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await FreightContractService.delete_contract(db, contract_id)
    return success()


@router.get("/{contract_id}/rate")
async def list_rates(
    contract_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await FreightRateService.list_by_contract(db, contract_id)
    return success(data=data)


@router.post("/{contract_id}/rate")
@operation_log(module="运价费率", action="新增", description="新增运价费率")
async def create_rate(
    request: Request,
    contract_id: int,
    data: FreightRateCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    contract = await FreightContractService.get_contract(db, contract_id)
    data.contractId = contract_id
    data.customerId = contract.customer_id
    rate = await FreightRateService.create_rate(db, data)
    return success(data=FreightRateOut.from_model(rate).model_dump())
