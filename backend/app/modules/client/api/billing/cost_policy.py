"""
成本政策 API（政策 CRUD + 政策下费用规则）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.billing.cost_policy import (
    CostPolicyCreate,
    CostPolicyOut,
    CostPolicyUpdate,
)
from app.modules.client.schemas.billing.cost_rule import CostRuleCreate, CostRuleOut
from app.modules.client.services.billing.cost_policy_service import CostPolicyService
from app.modules.client.services.billing.cost_rule_service import CostRuleService

router = APIRouter()


@router.get("")
async def page_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    scopeType: Optional[int] = None,
    carrierType: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CostPolicyService.page_policies(
        db, page=page, page_size=page_size, keyword=keyword,
        scope_type=scopeType, carrier_type=carrierType, status=status,
    )
    return success(data=data)


@router.get("/{policy_id}")
async def get_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    policy = await CostPolicyService.get_policy(db, policy_id)
    data = CostPolicyOut.from_model(policy).model_dump()
    data["rules"] = await CostRuleService.list_by_policy(db, policy_id)
    return success(data=data)


@router.post("")
@operation_log(module="成本政策", action="新增", description="新增成本政策")
async def create_policy(
    request: Request,
    data: CostPolicyCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    policy = await CostPolicyService.create_policy(
        db, data, current_user_id=current_user.user_id,
    )
    return success(data=CostPolicyOut.from_model(policy).model_dump())


@router.put("/{policy_id}")
@operation_log(module="成本政策", action="编辑", description="编辑成本政策")
async def update_policy(
    request: Request,
    policy_id: int,
    data: CostPolicyUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    policy = await CostPolicyService.update_policy(
        db, policy_id, data, current_user_id=current_user.user_id,
    )
    return success(data=CostPolicyOut.from_model(policy).model_dump())


@router.put("/{policy_id}/activate")
@operation_log(module="成本政策", action="激活", description="激活成本政策")
async def activate_policy(
    request: Request,
    policy_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    policy = await CostPolicyService.activate_policy(
        db, policy_id, current_user_id=current_user.user_id,
    )
    return success(data=CostPolicyOut.from_model(policy).model_dump())


@router.put("/{policy_id}/terminate")
@operation_log(module="成本政策", action="终止", description="终止成本政策")
async def terminate_policy(
    request: Request,
    policy_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    policy = await CostPolicyService.terminate_policy(
        db, policy_id, current_user_id=current_user.user_id,
    )
    return success(data=CostPolicyOut.from_model(policy).model_dump())


@router.delete("/{policy_id}")
@operation_log(module="成本政策", action="删除", description="删除成本政策")
async def delete_policy(
    request: Request,
    policy_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await CostPolicyService.delete_policy(db, policy_id)
    return success()


@router.get("/{policy_id}/rule")
async def list_rules(
    policy_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CostRuleService.list_by_policy(db, policy_id)
    return success(data=data)


@router.post("/{policy_id}/rule")
@operation_log(module="成本费用规则", action="新增", description="新增成本费用规则")
async def create_rule(
    request: Request,
    policy_id: int,
    data: CostRuleCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await CostPolicyService.get_policy(db, policy_id)
    rule = await CostRuleService.create_rule(
        db, policy_id, data, current_user_id=current_user.user_id,
    )
    return success(data=CostRuleOut.from_model(rule).model_dump())
