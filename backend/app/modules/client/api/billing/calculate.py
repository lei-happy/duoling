"""
企业端运费计算 API（试算）

兼容旧的单条试算 POST /billing/calculate，并新增一次传入所有 cargoes 的
批量试算 POST /billing/calculate/preview，返回 match_trace 用于前端可视化。
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.services.billing.billing_engine_service import BillingEngineService
from app.modules.client.services.billing.freight_calc_service import FreightCalcService

router = APIRouter()


class FreightCalcRequest(BaseModel):
    customerId: int
    originCode: str
    destinationCode: str
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int = 1
    billingDate: Optional[date] = None


@router.post("")
async def calculate_freight(
    data: FreightCalcRequest,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """单条货物试算（旧 API 兼容）"""
    result = await BillingEngineService.calculate_freight(
        db,
        customer_id=data.customerId,
        origin_code=data.originCode,
        destination_code=data.destinationCode,
        vehicle_brand=data.vehicleBrand,
        vehicle_model=data.vehicleModel,
        quantity=data.quantity or 1,
        billing_date=data.billingDate,
    )
    if result:
        return success(data=result.model_dump())
    return success(data=None)


# -------- 整单试算 --------

class PreviewCargoLine(BaseModel):
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    vin: Optional[str] = None
    quantity: int = Field(1, ge=1)


class PreviewRequest(BaseModel):
    customerId: int
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    origin: Optional[str] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    destination: Optional[str] = None
    cargoes: list[PreviewCargoLine] = Field(default_factory=list)
    billingDate: Optional[date] = None


def _decimal_to_float(d):
    if isinstance(d, Decimal):
        return float(d)
    return d


@router.post("/preview")
async def preview_freight(
    data: PreviewRequest,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """整单试算：一次传所有 cargoes，返回每行结果 + match_trace（dry_run）"""
    waybill = Waybill(
        id=0,
        waybill_no="__preview__",
        customer_id=data.customerId,
        origin=data.origin,
        origin_code=data.originCode,
        origin_region_id=data.originRegionId,
        destination=data.destination,
        destination_code=data.destinationCode,
        destination_region_id=data.destinationRegionId,
    )
    cargo_models: list[WaybillCargo] = []
    for idx, c in enumerate(data.cargoes or []):
        cargo_models.append(WaybillCargo(
            id=idx + 1,
            waybill_id=0,
            sort_order=idx,
            vehicle_brand=c.vehicleBrand,
            vehicle_model=c.vehicleModel,
            vin=c.vin,
            quantity=int(c.quantity or 1),
        ))

    summary = await FreightCalcService.preview_for_waybill(
        db, waybill, cargo_models, data.billingDate,
    )

    items = []
    for cr in summary.cargo_results:
        items.append({
            "waybillCargoId": cr.waybill_cargo_id,
            "calcStatus": cr.calc_status,
            "amount": _decimal_to_float(cr.amount),
            "unitPrice": _decimal_to_float(cr.unit_price),
            "billingMode": cr.billing_mode,
            "distanceKm": _decimal_to_float(cr.distance_km),
            "matchedContractId": cr.matched_contract.id if cr.matched_contract else None,
            "matchedContractNo": cr.matched_contract.contract_no if cr.matched_contract else None,
            "matchedRuleId": cr.matched_rule.id if cr.matched_rule else None,
            "matchedRuleVersion": cr.matched_rule.rule_version if cr.matched_rule else None,
            "direction": cr.direction,
            "originMatchLevel": cr.origin_match_level,
            "destinationMatchLevel": cr.destination_match_level,
            "modelMatchType": cr.model_match_type,
            "score": cr.score,
            "errorType": cr.error_type,
            "errorMessage": cr.error_message,
            "matchTrace": cr.match_trace,
        })

    return success(data={
        "calcStatus": summary.calc_status,
        "totalAmount": _decimal_to_float(summary.total_amount),
        "items": items,
    })

