"""
客户端菜单管理接口
管理 app_type='client' 的菜单，支持 feature_code 字段
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.client_menu import (
    ClientMenuCreate, ClientMenuUpdate,
)
from app.modules.console.services.client_menu_service import ClientMenuService

router = APIRouter()


@router.get("")
async def list_client_menus(
    title: Optional[str] = Query(None),
    path: Optional[str] = Query(None),
    authority: Optional[str] = Query(None),
    parentId: Optional[int] = Query(None),
    featureCode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询客户端菜单列表（扁平数组）"""
    items = await ClientMenuService.list_menus(
        db, title, path, authority, parentId, featureCode,
    )
    return success(data=[item.model_dump() for item in items])


@router.post("")
async def add_client_menu(
    data: ClientMenuCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增客户端菜单"""
    await ClientMenuService.create_menu(db, data)
    await db.commit()
    return success(message="添加成功")


@router.put("")
async def update_client_menu(
    data: ClientMenuUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改客户端菜单"""
    await ClientMenuService.update_menu(db, data)
    await db.commit()
    return success(message="修改成功")


@router.delete("/{menu_id}")
async def delete_client_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """删除客户端菜单"""
    await ClientMenuService.delete_menu(db, menu_id)
    await db.commit()
    return success(message="删除成功")
