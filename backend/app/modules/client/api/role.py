"""
企业端角色管理 API
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.role import (
    BizRoleCreate, BizRoleUpdate, BizRoleOut, BizRoleMenuAssign,
)
from app.modules.client.services.role_service import BizRoleService

router = APIRouter()


@router.get("")
async def list_roles(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取角色列表"""
    items = await BizRoleService.list_roles(db)
    return success(data=[item.model_dump() for item in items])


@router.post("")
async def create_role(
    data: BizRoleCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建角色"""
    role = await BizRoleService.create_role(db, data)
    return success(data=BizRoleOut.from_model(role).model_dump())


@router.put("/{role_id}")
async def update_role(
    role_id: int,
    data: BizRoleUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新角色"""
    role = await BizRoleService.update_role(db, role_id, data)
    return success(data=BizRoleOut.from_model(role).model_dump())


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除角色"""
    await BizRoleService.delete_role(db, role_id)
    return success()


@router.get("/{role_id}/menus")
async def get_role_menus(
    role_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取角色菜单ID列表"""
    menu_ids = await BizRoleService.get_role_menu_ids(db, role_id)
    return success(data=menu_ids)


@router.put("/{role_id}/menus")
async def assign_role_menus(
    role_id: int,
    data: BizRoleMenuAssign,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分配角色菜单"""
    await BizRoleService.assign_menus(db, role_id, data.menuIds)
    return success()
