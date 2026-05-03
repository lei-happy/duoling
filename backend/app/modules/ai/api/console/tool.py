"""Console 端：AI 工具管理（只读 + 启停 + 一键同步）"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.ai.schemas.console.tool import ToolStatusUpdate
from app.modules.ai.services.tool_service import ToolService

router = APIRouter()


@router.get("")
async def page_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await ToolService.page(
        db, page=page, page_size=page_size,
        keyword=keyword, category=category, status=status,
    )
    return success(data=data)


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data={"list": await ToolService.list_categories(db)})


@router.put("/{tool_id}/status")
async def update_status(
    tool_id: int,
    body: ToolStatusUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await ToolService.update_status(db, tool_id, body.status)
    return success(message="已更新")


@router.post("/sync")
async def sync_tools(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """把代码内 @register_tool 注册表同步到 ai_tool 表（手动触发）"""
    result = await ToolService.sync_from_registry(db)
    return success(data=result, message="工具同步完成")
