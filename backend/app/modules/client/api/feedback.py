"""
客户端意见反馈接口
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.client.schemas.feedback import FeedbackCreateIn
from app.modules.client.services.feedback_service import ClientFeedbackService

router = APIRouter()


@router.post("")
async def create_feedback(
    data: FeedbackCreateIn,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """提交意见反馈"""
    item = await ClientFeedbackService.create(
        db,
        data,
        user_id=current_user.user_id,
        tenant_code=current_user.tenant_code,
    )
    return success(
        data=item.model_dump(mode="json"),
        message="反馈已提交，我们会尽快处理",
    )


@router.get("")
async def list_feedbacks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None, description="处理状态"),
    feedback_type: Optional[int] = Query(None, description="反馈类型"),
    keyword: Optional[str] = Query(None, description="标题/内容关键词"),
    created_from: Optional[datetime] = Query(None, description="提交开始时间"),
    created_to: Optional[datetime] = Query(None, description="提交结束时间"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """我的反馈列表（管理员可见本租户全部）"""
    items, total = await ClientFeedbackService.list_feedbacks(
        db,
        user_id=current_user.user_id,
        user_type=current_user.user_type,
        tenant_code=current_user.tenant_code,
        page=page,
        limit=limit,
        status=status,
        feedback_type=feedback_type,
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
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """反馈详情"""
    item = await ClientFeedbackService.get_detail(
        db,
        feedback_id,
        user_id=current_user.user_id,
        user_type=current_user.user_type,
        tenant_code=current_user.tenant_code,
    )
    return success(data=item.model_dump(mode="json"))
