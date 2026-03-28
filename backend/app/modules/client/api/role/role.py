"""
企业端角色管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.client.schemas.role.role import (
    BizRoleCreate, BizRoleUpdate, BizRoleOut, BizRoleMenuAssign,
)
from app.modules.client.services.role.role_service import BizRoleService

router = APIRouter()


@router.get("/page")
async def page_roles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    roleName: Optional[str] = Query(None),
    roleCode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询角色"""
    result = await BizRoleService.page_roles(
        db, page=page, limit=limit,
        role_name=roleName, role_code=roleCode,
    )
    return success(data=result)


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


@router.put("")
async def update_role(
    data: BizRoleUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新角色"""
    role = await BizRoleService.update_role(db, data.roleId, data)
    return success(data=BizRoleOut.from_model(role).model_dump())


@router.delete("/batch")
async def batch_delete_roles(
    data: List[int] = Body(..., embed=False),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """批量删除角色"""
    await BizRoleService.batch_delete_roles(db, data)
    return success()


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
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取全部菜单并标记角色已分配的菜单（菜单来自平台库 sys_menu）"""
    menus = await BizRoleService.get_role_menus_with_checked(
        tenant_db, platform_db, role_id,
        tenant_code=current_user.tenant_code,
    )
    return success(data=menus)


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
