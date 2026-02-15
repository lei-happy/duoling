"""
产品更新日志公开查询接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.modules.console.schemas.changelog import ChangelogOut
from app.modules.console.services.changelog_service import ChangelogService

router = APIRouter()


@router.get("")
async def list_changelogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_platform_db),
):
    """获取产品更新记录列表（公开，仅已发布）"""
    items, total = await ChangelogService.get_public_changelog_list(
        db, page, page_size
    )
    return success(data={
        "list": [ChangelogOut.model_validate(v).model_dump() for v in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })
