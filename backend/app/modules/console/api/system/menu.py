"""
菜单管理接口
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.system.menu import MenuCreate, MenuUpdate
from app.modules.console.services.system.menu_service import MenuService

router = APIRouter()


@router.get("")
async def list_menus(
    title: Optional[str] = Query(None),
    path: Optional[str] = Query(None),
    authority: Optional[str] = Query(None),
    parentId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询菜单列表"""
    items = await MenuService.list_menus(db, title, path, authority, parentId)
    return success(data=[item.model_dump() for item in items])


@router.get("/page")
async def page_menus(
    page: int = Query(1),
    limit: int = Query(20),
    title: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询菜单"""
    result = await MenuService.page_menus(db, page, limit, title)
    return success(data=result)


@router.post("")
async def add_menu(
    data: MenuCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增菜单"""
    await MenuService.create_menu(db, data)
    await db.commit()
    return success(message="添加成功")


@router.put("")
async def update_menu(
    data: MenuUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改菜单"""
    await MenuService.update_menu(db, data)
    await db.commit()
    return success(message="修改成功")


@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """删除菜单"""
    await MenuService.delete_menu(db, menu_id)
    await db.commit()
    return success(message="删除成功")
