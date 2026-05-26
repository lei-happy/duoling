"""
社会运力池-审批 API

负责审批中心视角下的查询、统计、详情、通过、驳回。
社会运力档案 / 启用停用切换 / 结算账户管理在 list.py。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.schemas.capacity.social_capacity import (
    SocialCapacityApproveAction,
    SocialCapacityRejectAction,
)
from app.modules.client.services.capacity.social_capacity import (
    SocialCapacityService,
    APPROVAL_PENDING,
)


router = APIRouter()


async def _resolve_operator_name(
    db: AsyncSession, current_user: TokenData
) -> Optional[str]:
    if not current_user or not current_user.user_id:
        return None
    result = await db.execute(
        select(BizUser).where(
            BizUser.id == current_user.user_id,
            BizUser.is_deleted == 0,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    return user.real_name or user.nickname or user.phone


@router.get("")
async def page_for_approval(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    approvalStatus: Optional[int] = APPROVAL_PENDING,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """审核单分页查询（默认 approval_status=1）。"""
    data = await SocialCapacityService.page_for_approval(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        approval_status=approvalStatus,
    )
    return success(data=data)


@router.get("/stats")
async def approval_stats(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """审批工作台 KPI：待审核 / 已通过 / 已驳回 / 全部数量。"""
    data = await SocialCapacityService.approval_workbench_stats(db)
    return success(data=data)


@router.get("/{social_capacity_id}")
async def get_approval_detail(
    social_capacity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """审核详情：复用主体详情接口（含完整聚合 + 最近一条流水）。"""
    detail = await SocialCapacityService.get_detail(db, social_capacity_id)
    return success(data=detail.model_dump())


@router.post("/{social_capacity_id}/approve")
@operation_log(module="社会运力池", action="审核通过", description="社会运力审核通过")
async def approve_social_capacity(
    request: Request,
    social_capacity_id: int,
    data: Optional[SocialCapacityApproveAction] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    operator_name = await _resolve_operator_name(db, current_user)
    detail = await SocialCapacityService.approve(
        db,
        social_capacity_id,
        operator_user_id=current_user.user_id,
        operator_name=operator_name,
        remark=data.remark if data else None,
    )
    return success(data=detail.model_dump())


@router.post("/{social_capacity_id}/reject")
@operation_log(module="社会运力池", action="审核驳回", description="社会运力审核驳回")
async def reject_social_capacity(
    request: Request,
    social_capacity_id: int,
    data: SocialCapacityRejectAction,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    operator_name = await _resolve_operator_name(db, current_user)
    detail = await SocialCapacityService.reject(
        db,
        social_capacity_id,
        operator_user_id=current_user.user_id,
        operator_name=operator_name,
        remark=data.remark,
    )
    return success(data=detail.model_dump())
