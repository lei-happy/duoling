"""
社会运力池-列表 API

包含运力档案 CRUD、提交审核 / 撤回 / 启用停用黑名单切换、结算账户管理与
调度选择器等接口。审核动作 (approve/reject) 由 approval.py 提供。
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
    SocialCapacityCreate,
    SocialCapacityUpdate,
    SocialCapacityStatusUpdate,
    SocialCapacitySubmitAction,
    SocialCapacityAccountCreate,
    SocialCapacityAccountUpdate,
)
from app.modules.client.services.capacity.social_capacity import (
    SocialCapacityService,
    SocialCapacityAccountService,
    SocialCapacityAuditService,
)


router = APIRouter()


async def _resolve_operator_name(
    db: AsyncSession, current_user: TokenData
) -> Optional[str]:
    """根据 token 中的 user_id 查 biz_user.real_name / nickname，便于在审核流水里展示。"""
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


# =============================================================================
# 列表 / 详情 / 选择器 / 流水
# =============================================================================
@router.get("")
async def page_social_capacities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    approvalStatus: Optional[int] = None,
    status: Optional[int] = None,
    source: Optional[str] = None,
    ratingLevel: Optional[int] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await SocialCapacityService.page(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        approval_status=approvalStatus,
        status=status,
        source=source,
        rating_level=ratingLevel,
        sort=sort,
        order=order,
    )
    return success(data=data)


@router.get("/select")
async def list_for_dispatch(
    keyword: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await SocialCapacityService.list_for_dispatch(
        db, keyword=keyword, limit=limit
    )
    return success(data=data)


@router.get("/{social_capacity_id}")
async def get_social_capacity(
    social_capacity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    detail = await SocialCapacityService.get_detail(db, social_capacity_id)
    return success(data=detail.model_dump())


@router.get("/{social_capacity_id}/audit-history")
async def list_audit_history(
    social_capacity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await SocialCapacityAuditService.list_history(db, social_capacity_id)
    return success(data=data)


# =============================================================================
# 主体新增 / 编辑 / 删除
# =============================================================================
@router.post("")
@operation_log(module="社会运力池", action="新增", description="新增社会运力档案")
async def create_social_capacity(
    request: Request,
    data: SocialCapacityCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    detail = await SocialCapacityService.create(
        db, data=data, current_user_id=current_user.user_id
    )
    return success(data=detail.model_dump())


@router.put("/{social_capacity_id}")
@operation_log(module="社会运力池", action="编辑", description="编辑社会运力档案")
async def update_social_capacity(
    request: Request,
    social_capacity_id: int,
    data: SocialCapacityUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    detail = await SocialCapacityService.update(
        db,
        social_capacity_id,
        data=data,
        current_user_id=current_user.user_id,
    )
    return success(data=detail.model_dump())


@router.delete("/{social_capacity_id}")
@operation_log(module="社会运力池", action="删除", description="删除社会运力档案")
async def delete_social_capacity(
    request: Request,
    social_capacity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await SocialCapacityService.delete(db, social_capacity_id)
    return success()


# =============================================================================
# 状态机：提交 / 撤回 / 启用-停用-黑名单
# =============================================================================
@router.post("/{social_capacity_id}/submit")
@operation_log(module="社会运力池", action="提交审核", description="提交社会运力审核")
async def submit_social_capacity(
    request: Request,
    social_capacity_id: int,
    data: Optional[SocialCapacitySubmitAction] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    operator_name = await _resolve_operator_name(db, current_user)
    detail = await SocialCapacityService.submit(
        db,
        social_capacity_id,
        operator_user_id=current_user.user_id,
        operator_name=operator_name,
        remark=data.remark if data else None,
    )
    return success(data=detail.model_dump())


@router.post("/{social_capacity_id}/withdraw")
@operation_log(module="社会运力池", action="撤回审核", description="撤回社会运力审核")
async def withdraw_social_capacity(
    request: Request,
    social_capacity_id: int,
    data: Optional[SocialCapacitySubmitAction] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    operator_name = await _resolve_operator_name(db, current_user)
    detail = await SocialCapacityService.withdraw(
        db,
        social_capacity_id,
        operator_user_id=current_user.user_id,
        operator_name=operator_name,
        remark=data.remark if data else None,
    )
    return success(data=detail.model_dump())


@router.put("/{social_capacity_id}/status")
@operation_log(module="社会运力池", action="状态变更", description="启用/停用/黑名单切换")
async def update_status(
    request: Request,
    social_capacity_id: int,
    data: SocialCapacityStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    operator_name = await _resolve_operator_name(db, current_user)
    detail = await SocialCapacityService.update_status(
        db,
        social_capacity_id,
        target_status=data.status,
        operator_user_id=current_user.user_id,
        operator_name=operator_name,
        remark=data.remark,
    )
    return success(data=detail.model_dump())


# =============================================================================
# 结算账户
# =============================================================================
@router.get("/{social_capacity_id}/accounts")
async def list_accounts(
    social_capacity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await SocialCapacityAccountService.list_accounts(db, social_capacity_id)
    return success(data=data)


@router.post("/{social_capacity_id}/accounts")
@operation_log(module="社会运力池", action="新增账户", description="新增结算账户")
async def create_account(
    request: Request,
    social_capacity_id: int,
    data: SocialCapacityAccountCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    out = await SocialCapacityAccountService.create_account(
        db, social_capacity_id, data
    )
    return success(data=out.model_dump())


@router.put("/{social_capacity_id}/accounts/{account_id}")
@operation_log(module="社会运力池", action="编辑账户", description="编辑结算账户")
async def update_account(
    request: Request,
    social_capacity_id: int,
    account_id: int,
    data: SocialCapacityAccountUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    out = await SocialCapacityAccountService.update_account(
        db, social_capacity_id, account_id, data
    )
    return success(data=out.model_dump())


@router.delete("/{social_capacity_id}/accounts/{account_id}")
@operation_log(module="社会运力池", action="删除账户", description="删除结算账户")
async def delete_account(
    request: Request,
    social_capacity_id: int,
    account_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await SocialCapacityAccountService.delete_account(
        db, social_capacity_id, account_id
    )
    return success()


@router.post("/{social_capacity_id}/accounts/{account_id}/set-default")
@operation_log(module="社会运力池", action="设默认账户", description="设为默认结算账户")
async def set_default_account(
    request: Request,
    social_capacity_id: int,
    account_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    out = await SocialCapacityAccountService.set_default(
        db, social_capacity_id, account_id
    )
    return success(data=out.model_dump())
