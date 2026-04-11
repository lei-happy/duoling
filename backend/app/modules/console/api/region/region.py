"""
Console 端地区数据管理 API
操作平台库 sys_regions
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.region.region import (
    RegionCreate, RegionUpdate, RegionOut,
)
from app.modules.console.services.region.region_service import RegionService

router = APIRouter()


@router.get("/nav-tree")
async def get_nav_tree(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """获取省+市两级树结构（左侧导航面板）"""
    tree = await RegionService.get_nav_tree(db)
    return success(data=tree)


@router.get("/children")
async def page_children(
    pcode: int = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询指定节点的子地区列表"""
    result = await RegionService.page_children(
        db, pcode=pcode, page=page, limit=limit,
        name=name, status=status,
    )
    return success(data=result)


@router.get("/tree")
async def get_region_tree(
    pcode: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """获取地区子级列表（懒加载树）"""
    items = await RegionService.get_children(db, pcode=pcode)
    return success(data=[item.model_dump() for item in items])


@router.get("/search")
async def search_regions(
    name: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """按名称搜索地区"""
    items = await RegionService.search_regions(db, name=name, status=status)
    return success(data=[item.model_dump() for item in items])


@router.get("/{code}")
async def get_region(
    code: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """获取单条地区详情"""
    item = await RegionService.get_region(db, code)
    return success(data=item.model_dump())


@router.post("")
async def create_region(
    data: RegionCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增地区"""
    region = await RegionService.create_region(db, data)
    out = RegionOut.from_model(region)
    return success(data=out.model_dump())


@router.put("/{code}")
async def update_region(
    code: int,
    data: RegionUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """编辑地区"""
    region = await RegionService.update_region(db, code, data)
    out = RegionOut.from_model(region)
    return success(data=out.model_dump())


@router.delete("/{code}")
async def delete_region(
    code: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """软删除地区"""
    await RegionService.delete_region(db, code)
    return success()
