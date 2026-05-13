"""
企业端运价费率 API（更新/删除/重算受影响运单/版本历史/冲突预校验）
列表和新增通过合同嵌套路由 /billing/contract/{contract_id}/rate 访问
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.billing.freight_rate import (
    FreightRateOut,
    FreightRateUpdate,
)
from app.modules.client.services.billing.freight_calc_service import FreightCalcService
from app.modules.client.services.billing.freight_calc_task_service import (
    FreightCalcTaskService,
    TASK_RULE_CHANGED,
)
from app.modules.client.services.billing.freight_rate_service import FreightRateService
from app.modules.client.services.billing.freight_rule_conflict_service import (
    FreightRuleConflictService,
)

router = APIRouter()


@router.put("/{rate_id}")
@operation_log(module="运价费率", action="编辑", description="编辑运价费率")
async def update_rate(
    request: Request,
    rate_id: int,
    data: FreightRateUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    rate = await FreightRateService.update_rate(
        db, rate_id, data, current_user_id=current_user.user_id,
    )
    return success(data=FreightRateOut.from_model(rate).model_dump())


@router.delete("/{rate_id}")
@operation_log(module="运价费率", action="删除", description="删除运价费率")
async def delete_rate(
    request: Request,
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await FreightRateService.delete_rate(
        db, rate_id, current_user_id=current_user.user_id,
    )
    return success()


@router.post("/{rate_id}/recalculate-affected")
@operation_log(module="运价费率", action="重算受影响运单",
               description="对该运价规则触发受影响运单批量重算")
async def recalculate_affected(
    request: Request,
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    rate = await FreightRateService.get_rate(db, rate_id)
    waybill_ids = await FreightCalcService.find_affected_waybills_for_rule(
        db, rate,
    )
    enqueued = await FreightCalcTaskService.enqueue_many_waybills(
        db, waybill_ids,
        task_type=TASK_RULE_CHANGED,
        source_target_type="rule",
        source_target_id=rate.id,
        priority=8,
        triggered_by_user_id=current_user.user_id,
    )
    return success(data={
        "affectedWaybillCount": len(waybill_ids),
        "enqueuedTaskCount": enqueued,
    })


@router.get("/{rate_id}/version-history")
async def list_rate_version_history(
    rate_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    items = await FreightRateService.list_change_logs(db, rate_id)
    return success(data=items)


class _CheckConflictPayload(BaseModel):
    """运价规则冲突预校验入参（保存前由前端调）"""

    rateId: Optional[int] = None  # 编辑时传，新增时不传
    contractId: int
    customerId: int
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    priority: int = 0
    priceType: int = 0
    isBidirectional: int = 0
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None


@router.post("/check-conflict")
async def check_conflict(
    payload: _CheckConflictPayload,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """规则保存前预校验：返回潜在冲突列表与严重等级。"""
    conflicts = await FreightRuleConflictService.find_conflicts(
        db,
        exclude_rate_id=payload.rateId,
        contract_id=payload.contractId,
        customer_id=payload.customerId,
        origin_code=payload.originCode,
        origin_region_id=payload.originRegionId,
        destination_code=payload.destinationCode,
        destination_region_id=payload.destinationRegionId,
        brand_id=payload.brandId,
        series_id=payload.seriesId,
        priority=payload.priority,
        price_type=payload.priceType,
        is_bidirectional=payload.isBidirectional,
        effective_date=payload.effectiveDate,
        expiry_date=payload.expiryDate,
    )
    has_error = any(c.get("severity") == "error" for c in conflicts)
    return success(data={
        "conflicts": conflicts,
        "hasError": has_error,
        "count": len(conflicts),
    })
