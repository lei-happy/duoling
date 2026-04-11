"""
企业端运价费率 API（更新/删除，挂载于 /billing/rate）
列表和新增通过合同嵌套路由 /billing/contract/{contract_id}/rate 访问
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.billing.freight_rate import (
    FreightRateUpdate, FreightRateOut,
)
from app.modules.client.services.billing.freight_rate_service import FreightRateService

router = APIRouter()


@router.put("/{rate_id}")
@operation_log(module="运价费率", action="编辑", description="编辑运价费率")
async def update_rate(
    request: Request,
    rate_id: int,
    data: FreightRateUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    rate = await FreightRateService.update_rate(db, rate_id, data)
    return success(data=FreightRateOut.from_model(rate).model_dump())


@router.delete("/{rate_id}")
@operation_log(module="运价费率", action="删除", description="删除运价费率")
async def delete_rate(
    request: Request,
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await FreightRateService.delete_rate(db, rate_id)
    return success()
