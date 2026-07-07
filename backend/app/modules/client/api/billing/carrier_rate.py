"""
企业端承运价规则 API（更新/删除/重算受影响任务/版本历史）
列表和新增通过合同嵌套路由 /billing/carrier-contract/{contract_id}/rate 访问
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.billing.carrier_rate import (
    CarrierRateOut,
    CarrierRateUpdate,
)
from app.modules.client.services.billing.carrier_freight_calc_service import (
    CarrierFreightCalcService,
)
from app.modules.client.services.billing.carrier_freight_calc_task_service import (
    CarrierFreightCalcTaskService,
    TASK_RULE_CHANGED,
)
from app.modules.client.services.billing.carrier_rate_service import CarrierRateService

router = APIRouter()


@router.put("/{rate_id}")
@operation_log(module="承运价规则", action="编辑", description="编辑承运价规则")
async def update_rate(
    request: Request,
    rate_id: int,
    data: CarrierRateUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    rate = await CarrierRateService.update_rate(
        db, rate_id, data, current_user_id=current_user.user_id,
    )
    return success(data=CarrierRateOut.from_model(rate).model_dump())


@router.delete("/{rate_id}")
@operation_log(module="承运价规则", action="删除", description="删除承运价规则")
async def delete_rate(
    request: Request,
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await CarrierRateService.delete_rate(
        db, rate_id, current_user_id=current_user.user_id,
    )
    return success()


@router.post("/{rate_id}/recalculate-affected")
@operation_log(module="承运价规则", action="重算受影响任务",
               description="对该承运价规则触发受影响任务批量重算")
async def recalculate_affected(
    request: Request,
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    rate = await CarrierRateService.get_rate(db, rate_id)
    task_ids = await CarrierFreightCalcService.find_affected_tasks_for_rule(db, rate)
    enqueued = await CarrierFreightCalcTaskService.enqueue_many_tasks(
        db, task_ids,
        task_type=TASK_RULE_CHANGED,
        source_target_type="rule",
        source_target_id=rate.id,
        priority=8,
        triggered_by_user_id=current_user.user_id,
    )
    return success(data={
        "affectedTaskCount": len(task_ids),
        "enqueuedTaskCount": enqueued,
    })


@router.get("/{rate_id}/version-history")
async def list_rate_version_history(
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    items = await CarrierRateService.list_change_logs(db, rate_id)
    return success(data=items)
