"""
角色菜单分配接口
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.system.role import RoleMenuUpdate
from app.modules.console.services.system.role_service import RoleService

router = APIRouter()


@router.get("/{role_id}")
async def get_role_menus(
    role_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """获取角色已分配的菜单 ID 列表"""
    menu_ids = await RoleService.get_role_menus(db, role_id)
    return success(data=menu_ids)


@router.put("/{role_id}")
async def update_role_menus(
    role_id: int,
    data: RoleMenuUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改角色菜单分配"""
    await RoleService.update_role_menus(db, role_id, data.menuIds)
    return success(message="分配成功")
