"""
任务成本计算 API（试算 / 重算 / 结果查询 / 元数据）
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import BizException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.models.billing.task_cost_result import (
    TaskCostResult,
    TaskCostResultItem,
)
from app.modules.client.schemas.billing.task_cost import (
    TaskCostPreviewRequest,
    TaskCostItemOut,
    TaskCostResultOut,
)
from app.modules.client.services.billing.conditions import describe_all
from app.modules.client.services.billing.cost_constants import FEE_TYPES, PRICING_METHODS
from app.modules.client.services.billing.task_cost_calc_service import (
    TaskCostCalcService,
    TaskCostSummary,
)

router = APIRouter()


def _summary_to_out(summary: TaskCostSummary) -> TaskCostResultOut:
    items = []
    for it in summary.items:
        if it.fee_type == "__task__":
            continue
        items.append(TaskCostItemOut(
            feeType=it.fee_type,
            feeName=it.fee_name,
            direction=it.direction,
            payeeType=it.payee_type,
            pricingMethod=it.pricing_method,
            unitPrice=float(it.unit_price) if it.unit_price is not None else None,
            quantity=float(it.quantity) if it.quantity is not None else None,
            distanceKm=float(it.distance_km) if it.distance_km is not None else None,
            amount=float(it.amount),
            matchedPolicyId=it.matched_policy_id,
            matchedRuleId=it.matched_rule_id,
            matchedRuleVersion=it.matched_rule_version,
            matchScore=it.match_score,
            calcStatus=it.calc_status,
            errorType=it.error_type,
            errorMessage=it.error_message,
            matchTrace=it.match_trace,
        ))
    return TaskCostResultOut(
        taskId=summary.task_id,
        totalCostAmount=float(summary.total_cost_amount),
        totalAdditionAmount=float(summary.total_addition_amount),
        totalDeductionAmount=float(summary.total_deduction_amount),
        calcStatus=summary.calc_status,
        carrierType=summary.carrier_type,
        payeeType=summary.payee_type,
        payeeId=summary.payee_id,
        payeeName=summary.payee_name,
        errorMessage=summary.error_message,
        items=items,
    )


@router.post("/task-cost/preview")
async def preview_task_cost(
    payload: TaskCostPreviewRequest,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """试算任务成本（不落库）。传 taskId 用任务事实数据，否则用散字段。"""
    if payload.taskId:
        task = await TaskCostCalcService._load_task(db, payload.taskId)
        if not task:
            raise BizException("任务不存在")
        summary = await TaskCostCalcService.preview_for_task(
            db, task, billing_date=payload.transportDate,
        )
    else:
        vehicles = [v.model_dump() for v in (payload.vehicles or [])]
        summary = await TaskCostCalcService.preview_adhoc(
            db,
            carrier_type=payload.carrierType,
            capacity_id=payload.capacityId,
            carrier_id=payload.carrierId,
            driver_id=payload.driverId,
            origin_region_id=payload.originRegionId,
            destination_region_id=payload.destinationRegionId,
            total_quantity=payload.totalQuantity,
            vehicles=vehicles,
            distance_km=payload.distanceKm,
            billing_date=payload.transportDate,
        )
    return success(data=_summary_to_out(summary).model_dump())


@router.post("/task/{task_id}/cost/recalculate")
@operation_log(module="成本引擎", action="重算任务成本", description="手动重算任务应付成本")
async def recalculate_task_cost(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    summary = await TaskCostCalcService.calculate_and_persist(
        db, task_id,
        triggered_by="manual_recalc",
        triggered_user_id=current_user.user_id,
    )
    return success(data=_summary_to_out(summary).model_dump())


@router.get("/task/{task_id}/cost-result")
async def get_task_cost_result(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TaskCostResult).where(
            TaskCostResult.task_id == task_id,
            TaskCostResult.is_active == 1,
            TaskCostResult.is_deleted == 0,
        ).order_by(TaskCostResult.id.desc()).limit(1)
    )
    result = r.scalar_one_or_none()
    if not result:
        return success(data=None)

    ri = await db.execute(
        select(TaskCostResultItem).where(
            TaskCostResultItem.result_id == result.id,
            TaskCostResultItem.is_deleted == 0,
        ).order_by(TaskCostResultItem.id.asc())
    )
    items = []
    for it in ri.scalars().all():
        items.append(TaskCostItemOut(
            feeType=it.fee_type,
            feeName=it.fee_name,
            direction=it.direction,
            payeeType=it.payee_type,
            pricingMethod=it.pricing_method,
            unitPrice=float(it.unit_price) if it.unit_price is not None else None,
            quantity=float(it.quantity) if it.quantity is not None else None,
            distanceKm=float(it.distance_km) if it.distance_km is not None else None,
            amount=float(it.amount),
            matchedPolicyId=it.matched_policy_id,
            matchedRuleId=it.matched_rule_id,
            matchedRuleVersion=it.matched_rule_version,
            matchScore=it.match_score,
            calcStatus=it.calc_status,
            errorType=it.error_type,
            errorMessage=it.error_message,
            matchTrace=it.match_trace_json,
        ).model_dump())

    data = TaskCostResultOut(
        taskId=task_id,
        totalCostAmount=float(result.total_cost_amount),
        totalAdditionAmount=float(result.total_addition_amount),
        totalDeductionAmount=float(result.total_deduction_amount),
        calcStatus=result.calc_status,
        carrierType=result.carrier_type,
        payeeType=result.payee_type,
        payeeId=result.payee_id,
        payeeName=result.payee_name,
        errorMessage=result.error_message,
        items=[],
    ).model_dump()
    data["items"] = items
    data["calcTime"] = result.calc_time.isoformat() if result.calc_time else None
    data["calcEngineVersion"] = result.calc_engine_version
    return success(data=data)


@router.get("/cost-meta")
async def get_cost_meta(_=Depends(get_current_user)):
    """费用类型 / 计价方式 / 条件类型元数据，供前端下拉与动态条件构建器。"""
    return success(data={
        "feeTypes": FEE_TYPES,
        "pricingMethods": PRICING_METHODS,
        "conditionTypes": describe_all(),
    })
