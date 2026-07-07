"""
成本费用规则 API（更新 / 删除 / 冲突检测 / 受影响任务重算）
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.billing.cost_rule import CostRuleOut, CostRuleUpdate
from app.modules.client.services.billing.cost_rule_conflict_service import (
    CostRuleConflictService,
)
from app.modules.client.services.billing.cost_rule_service import CostRuleService

router = APIRouter()


@router.get("")
async def list_rules_cross_policy(
    feeType: Optional[str] = Query(None),
    scopeType: Optional[int] = Query(None),
    carrierType: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """费用中心：跨政策查询全部成本费用规则（附所属政策信息）。"""
    data = await CostRuleService.list_rules_cross_policy(
        db,
        fee_type=feeType,
        scope_type=scopeType,
        carrier_type=carrierType,
        status=status,
        keyword=keyword,
    )
    return success(data=data)


@router.put("/{rule_id}")
@operation_log(module="成本费用规则", action="编辑", description="编辑成本费用规则")
async def update_rule(
    request: Request,
    rule_id: int,
    data: CostRuleUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    rule = await CostRuleService.update_rule(
        db, rule_id, data, current_user_id=current_user.user_id,
    )
    return success(data=CostRuleOut.from_model(rule).model_dump())


@router.delete("/{rule_id}")
@operation_log(module="成本费用规则", action="删除", description="删除成本费用规则")
async def delete_rule(
    request: Request,
    rule_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await CostRuleService.delete_rule(
        db, rule_id, current_user_id=current_user.user_id,
    )
    return success()


class _CheckConflictPayload(BaseModel):
    ruleId: Optional[int] = None
    policyId: int
    feeType: str
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    priceType: int = 0
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None


@router.post("/check-conflict")
async def check_conflict(
    payload: _CheckConflictPayload,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CostRuleConflictService.check_conflict(
        db,
        rule_id=payload.ruleId,
        policy_id=payload.policyId,
        fee_type=payload.feeType,
        origin_region_id=payload.originRegionId,
        destination_region_id=payload.destinationRegionId,
        brand_id=payload.brandId,
        series_id=payload.seriesId,
        price_type=payload.priceType,
        effective_date=payload.effectiveDate,
        expiry_date=payload.expiryDate,
    )
    return success(data=data)


@router.post("/{rule_id}/recalculate-affected")
@operation_log(module="成本费用规则", action="重算受影响任务", description="按规则触发受影响任务重算")
async def recalculate_affected(
    request: Request,
    rule_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    data = await CostRuleService.recalculate_affected(
        db, rule_id, current_user_id=current_user.user_id,
    )
    return success(data=data)
