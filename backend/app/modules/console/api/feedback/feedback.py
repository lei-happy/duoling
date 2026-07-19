"""
意见反馈管理接口（Console）
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.console.schemas.feedback.feedback import FeedbackHandleIn
from app.modules.console.services.feedback.feedback_service import FeedbackService

router = APIRouter()


@router.get("")
async def list_feedbacks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    status: Optional[int] = Query(None, description="处理状态"),
    feedback_type: Optional[int] = Query(None, description="反馈类型"),
    tenant_code: Optional[str] = Query(None, description="租户编码"),
    keyword: Optional[str] = Query(None, description="标题/内容关键词"),
    created_from: Optional[datetime] = Query(None, description="提交开始时间"),
    created_to: Optional[datetime] = Query(None, description="提交结束时间"),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """分页查询全平台意见反馈"""
    items, total = await FeedbackService.list_feedbacks(
        db,
        page=page,
        limit=limit,
        status=status,
        feedback_type=feedback_type,
        tenant_code=tenant_code,
        keyword=keyword,
        created_from=created_from,
        created_to=created_to,
    )
    return success(data={
        "list": [item.model_dump(mode="json") for item in items],
        "total": total,
        "page": page,
        "limit": limit,
    })


@router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取反馈详情"""
    item = await FeedbackService.get_detail(db, feedback_id)
    return success(data=item.model_dump(mode="json"))


@router.put("/{feedback_id}/handle")
async def handle_feedback(
    feedback_id: int,
    data: FeedbackHandleIn,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新处理状态与回复"""
    handler_name = await FeedbackService.resolve_handler_name(
        db, current_user.user_id
    )
    item = await FeedbackService.handle_feedback(
        db,
        feedback_id,
        data,
        handler_id=current_user.user_id,
        handler_name=handler_name,
    )
    return success(
        data=item.model_dump(mode="json"),
        message="已更新处理结果",
    )
