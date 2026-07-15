"""
客户端工作台 - 快捷操作目录

下发运营在 Console 配置的"支持快捷操作"的菜单目录，
前端据此按用户权限/产品功能过滤后展示与管理。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.client.services.quick_action_service import QuickActionService

router = APIRouter()


@router.get("")
async def list_quick_action_registry(
    _: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """快捷操作目录（运营在客户端菜单里配置）"""
    items = await QuickActionService.list_registry(db)
    return success(data=items)
