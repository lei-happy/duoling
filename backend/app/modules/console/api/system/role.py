"""
角色管理接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.system.role import RoleCreate, RoleUpdate
from app.modules.console.services.system.role_service import RoleService

router = APIRouter()


@router.get("/page")
async def page_roles(
    page: int = Query(1),
    limit: int = Query(20),
    roleName: Optional[str] = Query(None),
    roleCode: Optional[str] = Query(None),
    comments: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询角色"""
    result = await RoleService.page_roles(db, page, limit, roleName, roleCode, comments)
    return success(data=result)


@router.get("")
async def list_roles(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询角色列表"""
    items = await RoleService.list_roles(db)
    return success(data=[item.model_dump() for item in items])


@router.post("")
async def add_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增角色"""
    await RoleService.create_role(db, data)
    await db.commit()
    return success(message="添加成功")


@router.put("")
async def update_role(
    data: RoleUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改角色"""
    await RoleService.update_role(db, data)
    await db.commit()
    return success(message="修改成功")


@router.delete("/batch")
async def batch_delete_roles(
    ids: List[int] = Body(..., embed=False),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量删除角色"""
    await RoleService.batch_delete(db, ids)
    await db.commit()
    return success(message="删除成功")


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """删除角色"""
    await RoleService.delete_role(db, role_id)
    await db.commit()
    return success(message="删除成功")
