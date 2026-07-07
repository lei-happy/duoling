"""
承运商运费计算 API（试算 / 重算 / 结果查询）
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
from app.modules.client.models.billing.carrier_freight_result import (
    CarrierFreightResult,
    CarrierFreightResultDetail,
)
from app.modules.client.schemas.billing.carrier_freight import (
    CarrierFreightItemOut,
    CarrierFreightPreviewRequest,
    CarrierFreightResultOut,
)
from app.modules.client.services.billing.carrier_freight_calc_service import (
    CarrierFreightCalcService,
    CarrierFreightSummary,
)

router = APIRouter()


def _summary_to_out(summary: CarrierFreightSummary) -> CarrierFreightResultOut:
    items = []
    for gr in summary.groups:
        if gr.group_key == "__task__":
            continue
        items.append(CarrierFreightItemOut(
            brandId=gr.brand_id,
            seriesId=gr.series_id,
            vehicleBrand=gr.vehicle_brand,
            vehicleModel=gr.vehicle_model,
            quantity=int(gr.quantity or 0),
            matchedContractId=(gr.matched_contract.id if gr.matched_contract else None),
            matchedRuleId=(gr.matched_rule.id if gr.matched_rule else None),
            matchedRuleVersion=(gr.matched_rule.rule_version if gr.matched_rule else None),
            direction=gr.direction,
            modelMatchType=gr.model_match_type,
            originMatchLevel=gr.origin_match_level,
            destinationMatchLevel=gr.destination_match_level,
            unitPrice=float(gr.unit_price) if gr.unit_price is not None else None,
            billingMode=gr.billing_mode,
            distanceKm=float(gr.distance_km) if gr.distance_km is not None else None,
            amount=float(gr.amount),
            matchScore=gr.score,
            calcStatus=gr.calc_status,
            errorType=gr.error_type,
            errorMessage=gr.error_message,
            matchTrace=gr.match_trace,
        ))
    return CarrierFreightResultOut(
        taskId=summary.task_id,
        totalAmount=float(summary.total_amount),
        calcStatus=summary.calc_status,
        carrierId=summary.carrier_id,
        carrierName=summary.carrier_name,
        matchedContractId=summary.matched_contract_id,
        errorMessage=summary.error_message,
        items=items,
    )


@router.post("/carrier-freight/preview")
async def preview_carrier_freight(
    payload: CarrierFreightPreviewRequest,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """试算承运商运费（不落库）。传 taskId 用任务事实数据，否则用散字段。"""
    if payload.taskId:
        task = await CarrierFreightCalcService._load_task(db, payload.taskId)
        if not task:
            raise BizException("任务不存在")
        summary = await CarrierFreightCalcService.preview_for_task(
            db, task, billing_date=payload.transportDate,
        )
    else:
        vehicles = [v.model_dump() for v in (payload.vehicles or [])]
        summary = await CarrierFreightCalcService.preview_adhoc(
            db,
            carrier_id=payload.carrierId,
            origin_region_id=payload.originRegionId,
            destination_region_id=payload.destinationRegionId,
            total_quantity=payload.totalQuantity,
            vehicles=vehicles,
            billing_date=payload.transportDate,
        )
    return success(data=_summary_to_out(summary).model_dump())


@router.post("/task/{task_id}/carrier-freight/recalculate")
@operation_log(module="承运运费引擎", action="重算承运运费", description="手动重算任务承运运费")
async def recalculate_carrier_freight(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    summary = await CarrierFreightCalcService.calculate_and_persist(
        db, task_id,
        triggered_by="manual_recalc",
        triggered_user_id=current_user.user_id,
    )
    return success(data=_summary_to_out(summary).model_dump())


@router.get("/task/{task_id}/carrier-freight-result")
async def get_carrier_freight_result(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(CarrierFreightResult).where(
            CarrierFreightResult.task_id == task_id,
            CarrierFreightResult.is_active == 1,
            CarrierFreightResult.is_deleted == 0,
        ).order_by(CarrierFreightResult.id.desc()).limit(1)
    )
    result = r.scalar_one_or_none()
    if not result:
        return success(data=None)

    ri = await db.execute(
        select(CarrierFreightResultDetail).where(
            CarrierFreightResultDetail.result_id == result.id,
            CarrierFreightResultDetail.is_deleted == 0,
        ).order_by(CarrierFreightResultDetail.id.asc())
    )
    items = []
    for it in ri.scalars().all():
        items.append(CarrierFreightItemOut(
            brandId=it.brand_id,
            seriesId=it.series_id,
            vehicleBrand=it.vehicle_brand,
            vehicleModel=it.vehicle_model,
            quantity=int(it.quantity or 0),
            matchedContractId=it.matched_contract_id,
            matchedRuleId=it.matched_rule_id,
            matchedRuleVersion=it.matched_rule_version,
            direction=it.direction,
            modelMatchType=it.model_match_type,
            originMatchLevel=it.origin_match_level,
            destinationMatchLevel=it.destination_match_level,
            unitPrice=float(it.unit_price) if it.unit_price is not None else None,
            billingMode=it.billing_mode,
            distanceKm=float(it.distance_km) if it.distance_km is not None else None,
            amount=float(it.amount),
            matchScore=it.match_score,
            calcStatus=it.calc_status,
            errorType=it.error_type,
            errorMessage=it.error_message,
            matchTrace=it.match_trace_json,
        ).model_dump())

    data = CarrierFreightResultOut(
        taskId=task_id,
        totalAmount=float(result.total_amount),
        calcStatus=result.calc_status,
        carrierId=result.carrier_id,
        carrierName=result.carrier_name,
        matchedContractId=result.matched_contract_id,
        errorMessage=result.error_message,
        items=[],
    ).model_dump()
    data["items"] = items
    data["calcTime"] = result.calc_time.isoformat() if result.calc_time else None
    data["calcEngineVersion"] = result.calc_engine_version
    return success(data=data)
