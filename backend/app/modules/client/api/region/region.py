"""
企业端地区数据管理 API
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.region.region import (
    RegionCreate, RegionUpdate, RegionOut,
)
from app.modules.client.services.region.region_service import RegionService

router = APIRouter()


@router.get("/nav-tree")
async def get_nav_tree(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取省+市两级树结构（左侧导航面板）"""
    tree = await RegionService.get_nav_tree(db)
    return success(data=tree)


@router.get("/children")
async def page_children(
    parentCode: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    source: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询指定节点的子地区列表（右侧表格）"""
    result = await RegionService.page_children(
        db, parent_code=parentCode, page=page, limit=limit,
        name=name, source=source,
    )
    return success(data=result)


@router.get("/tree")
async def get_region_tree(
    parentCode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取地区子级列表（懒加载树）"""
    items = await RegionService.get_children(db, parent_code=parentCode)
    return success(data=[item.model_dump() for item in items])


@router.get("/search")
async def search_regions(
    name: Optional[str] = Query(None),
    source: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """按名称搜索地区"""
    items = await RegionService.search_regions(db, name=name, source=source)
    return success(data=[item.model_dump() for item in items])


@router.get("/{region_id}")
async def get_region(
    region_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取单条地区详情"""
    item = await RegionService.get_region(db, region_id)
    return success(data=item.model_dump())


@router.post("")
@operation_log(module="地区数据", action="新增", description="新增自定义地区")
async def create_region(
    request: Request,
    data: RegionCreate,
    db: AsyncSession = Depends(get_tenant_db),
    user=Depends(get_current_user),
):
    """新增自定义地区"""
    region = await RegionService.create_region(db, data, user_id=user.user_id)
    out = RegionOut.from_model(region)
    return success(data=out.model_dump())


@router.put("/{region_id}")
@operation_log(module="地区数据", action="编辑", description="编辑自定义地区")
async def update_region(
    request: Request,
    region_id: int,
    data: RegionUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """修改自定义地区"""
    region = await RegionService.update_region(db, region_id, data)
    out = RegionOut.from_model(region)
    return success(data=out.model_dump())


@router.delete("/{region_id}")
@operation_log(module="地区数据", action="删除", description="删除自定义地区")
async def delete_region(
    request: Request,
    region_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """软删除自定义地区"""
    await RegionService.delete_region(db, region_id)
    return success()
