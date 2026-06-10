"""审批中心 - 待办 / 申请 / 记录 / 审批动作 API

完整前缀：/api/client/approval
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
from app.modules.client.schemas.approval.instance import (
    ApprovalActionIn,
    ApprovalRejectIn,
    WithdrawIn,
    TransferIn,
    AddSignIn,
    CcIn,
)
from app.modules.client.services.approval import (
    ApprovalEngine,
    ApprovalQueryService,
)

router = APIRouter()


async def _operator_dept_id(db: AsyncSession, user_id: int) -> Optional[int]:
    return (
        await db.execute(
            select(BizUser.department_id).where(
                BizUser.id == user_id, BizUser.is_deleted == 0
            )
        )
    ).scalar_one_or_none()


# ---------------------------------------------------------------------------
# 列表
# ---------------------------------------------------------------------------
@router.get("/pending")
async def list_pending(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    bizType: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """我的待办。"""
    data = await ApprovalQueryService.list_pending(
        db, user_id=current_user.user_id, page=page, page_size=page_size,
        biz_type=bizType, keyword=keyword,
    )
    return success(data=data)


@router.get("/pending/count")
async def pending_count(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """待办数量（菜单红点）。"""
    count = await ApprovalQueryService.pending_count(db, user_id=current_user.user_id)
    return success(data={"count": count})


@router.get("/initiated")
async def list_initiated(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    status: Optional[int] = None,
    bizType: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """我的申请。"""
    data = await ApprovalQueryService.list_initiated(
        db, user_id=current_user.user_id, page=page, page_size=page_size,
        status=status, biz_type=bizType, keyword=keyword,
    )
    return success(data=data)


@router.get("/history")
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    status: Optional[int] = None,
    bizType: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """审批记录。"""
    data = await ApprovalQueryService.list_history(
        db, page=page, page_size=page_size, status=status, biz_type=bizType, keyword=keyword,
    )
    return success(data=data)


@router.get("/instance/{instance_id}")
async def get_instance_detail(
    instance_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """审批实例详情（含节点/流水/抄送 + 当前用户可处理待办）。"""
    detail = await ApprovalQueryService.get_detail(
        db, instance_id=instance_id, current_user_id=current_user.user_id
    )
    return success(data=detail.model_dump())


# ---------------------------------------------------------------------------
# 审批动作
# ---------------------------------------------------------------------------
@router.post("/task/{task_id}/agree")
@operation_log(module="审批中心", action="同意", description="审批同意")
async def agree(
    request: Request,
    task_id: int,
    data: Optional[ApprovalActionIn] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await ApprovalEngine.agree(
        db, task_id=task_id, operator_id=current_user.user_id,
        comment=data.comment if data else None,
        attachments=data.attachments if data else None,
    )
    return success(message="已同意")


@router.post("/task/{task_id}/reject")
@operation_log(module="审批中心", action="拒绝", description="审批拒绝")
async def reject(
    request: Request,
    task_id: int,
    data: ApprovalRejectIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await ApprovalEngine.reject(
        db, task_id=task_id, operator_id=current_user.user_id,
        comment=data.comment, attachments=data.attachments,
    )
    return success(message="已拒绝")


@router.post("/task/{task_id}/transfer")
@operation_log(module="审批中心", action="转审", description="审批转审")
async def transfer(
    request: Request,
    task_id: int,
    data: TransferIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await ApprovalEngine.transfer(
        db, task_id=task_id, operator_id=current_user.user_id,
        target_user_id=data.targetUserId, comment=data.comment,
    )
    return success(message="已转审")


@router.post("/task/{task_id}/add-sign")
@operation_log(module="审批中心", action="加签", description="审批加签")
async def add_sign(
    request: Request,
    task_id: int,
    data: AddSignIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await ApprovalEngine.add_sign(
        db, task_id=task_id, operator_id=current_user.user_id,
        target_user_id=data.targetUserId, mode=data.mode, comment=data.comment,
    )
    return success(message="已加签")


@router.post("/instance/{instance_id}/withdraw")
@operation_log(module="审批中心", action="撤回", description="审批撤回")
async def withdraw(
    request: Request,
    instance_id: int,
    data: Optional[WithdrawIn] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await ApprovalEngine.withdraw(
        db, instance_id=instance_id, operator_id=current_user.user_id,
        reason=data.reason if data else None,
    )
    return success(message="已撤回")


@router.post("/instance/{instance_id}/cc")
@operation_log(module="审批中心", action="抄送", description="审批抄送")
async def cc(
    request: Request,
    instance_id: int,
    data: CcIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await ApprovalEngine.cc(
        db, instance_id=instance_id, operator_id=current_user.user_id,
        target_user_ids=data.targetUserIds,
    )
    return success(message="已抄送")
