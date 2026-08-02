"""
企业端角色管理 API
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.role.role import (
    BizRoleCreate, BizRoleUpdate, BizRoleOut, BizRoleMenuAssign,
)
from app.modules.client.services.role.role_service import BizRoleService
from app.modules.client.services.user.platform_user_sync import BizPlatformUserSync

router = APIRouter()


@router.get("/page")
async def page_roles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    roleName: Optional[str] = Query(None),
    roleCode: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询角色"""
    result = await BizRoleService.page_roles(
        db, page=page, limit=limit,
        role_name=roleName, role_code=roleCode,
        sort=sort, order=order,
    )
    return success(data=result)


@router.get("")
async def list_roles(
    roleName: Optional[str] = Query(None),
    roleCode: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取角色列表（含关联用户数、已授权菜单数）"""
    items = await BizRoleService.list_roles(
        db,
        role_name=roleName,
        role_code=roleCode,
        sort=sort,
        order=order,
    )
    return success(data=[item.model_dump() for item in items])


@router.post("")
@operation_log(module="角色管理", action="新增", description="新增角色")
async def create_role(
    request: Request,
    data: BizRoleCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建角色"""
    role = await BizRoleService.create_role(db, data)
    return success(data=BizRoleOut.from_model(role).model_dump())


@router.put("")
@operation_log(module="角色管理", action="编辑", description="编辑角色")
async def update_role(
    request: Request,
    data: BizRoleUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新角色"""
    role = await BizRoleService.update_role(db, data.roleId, data)
    return success(data=BizRoleOut.from_model(role).model_dump())


@router.delete("/{role_id}")
@operation_log(module="角色管理", action="删除", description="删除角色")
async def delete_role(
    request: Request,
    role_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除角色"""
    await BizRoleService.delete_role(db, role_id)
    return success()


@router.get("/{role_id}/users")
async def list_role_users(
    role_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """查询拥有该角色的员工列表"""
    items = await BizRoleService.list_role_users(db, role_id)
    return success(data=items)


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
@operation_log(module="角色管理", action="分配菜单", description="分配角色菜单权限")
async def assign_role_menus(
    request: Request,
    role_id: int,
    data: BizRoleMenuAssign,
    db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """分配角色菜单（租户库 biz_role_menu + 平台库镜像 sys_role_menu 双写）"""
    await BizRoleService.assign_menus(db, role_id, data.menuIds)
    # 同步到平台库镜像角色，确保登录算菜单（走 sys_role_menu）生效
    if current_user.tenant_code:
        await BizPlatformUserSync.sync_role_menus(
            platform_db, db, current_user.tenant_code, role_id, data.menuIds
        )
    return success()
