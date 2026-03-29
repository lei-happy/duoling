"""
产品更新日志管理接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.changelog.changelog import (
    ChangelogCreate, ChangelogUpdate, ChangelogOut,
)
from app.modules.console.services.changelog.changelog_service import ChangelogService

router = APIRouter()


@router.get("")
async def list_changelogs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    status: Optional[int] = Query(None, description="状态筛选 0-停用 1-已发布"),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取更新记录列表"""
    items, total = await ChangelogService.get_changelog_list(
        db, page, limit, status
    )
    return success(data={
        "list": [ChangelogOut.model_validate(v).model_dump() for v in items],
        "total": total,
        "page": page,
        "limit": limit,
    })


@router.get("/{changelog_id}")
async def get_changelog(
    changelog_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取更新记录详情"""
    changelog = await ChangelogService.get_changelog_by_id(db, changelog_id)
    if not changelog:
        return fail("更新记录不存在")
    return success(data=ChangelogOut.model_validate(changelog).model_dump())


@router.post("")
async def create_changelog(
    data: ChangelogCreate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """创建更新记录"""
    changelog = await ChangelogService.create_changelog(db, data)
    return success(
        data=ChangelogOut.model_validate(changelog).model_dump(),
        message="创建成功",
    )


@router.put("/{changelog_id}")
async def update_changelog(
    changelog_id: int,
    data: ChangelogUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新更新记录"""
    changelog = await ChangelogService.update_changelog(db, changelog_id, data)
    return success(
        data=ChangelogOut.model_validate(changelog).model_dump(),
        message="更新成功",
    )


@router.delete("/{changelog_id}")
async def delete_changelog(
    changelog_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """删除更新记录"""
    await ChangelogService.delete_changelog(db, changelog_id)
    return success(message="删除成功")
