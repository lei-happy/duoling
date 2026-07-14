"""
客户端工作台 - 产品版本升级说明
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.client.schemas.workbench.changelog import (
    ChangelogItem,
    ChangelogListOut,
    ChangelogPopupOut,
    ChangelogReadIn,
)
from app.modules.client.services.changelog_service import ClientChangelogService

router = APIRouter()


@router.get("")
async def list_changelogs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """已发布的版本升级说明列表（供租户端查看历史更新）"""
    items, total = await ClientChangelogService.list_published(db, page, limit)
    return success(data=ChangelogListOut(
        list=[ChangelogItem.model_validate(v) for v in items],
        total=total,
        page=page,
        limit=limit,
    ).model_dump(mode="json"))


@router.get("/popup")
async def list_popup_changelogs(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """当前用户尚未读过、需要强制弹框的版本升级说明"""
    items = await ClientChangelogService.list_unread_popups(db, current_user.user_id)
    return success(data=ChangelogPopupOut(
        items=[ChangelogItem.model_validate(v) for v in items],
    ).model_dump(mode="json"))


@router.post("/read")
async def mark_changelogs_read(
    data: ChangelogReadIn,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """标记版本升级说明为已读，下次不再强制弹框"""
    await ClientChangelogService.mark_read(
        db,
        changelog_ids=data.changelog_ids,
        user_id=current_user.user_id,
        tenant_code=current_user.tenant_code,
    )
    return success(message="ok")
