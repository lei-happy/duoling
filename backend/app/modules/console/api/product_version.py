"""
产品版本管理接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.product_version import (
    ProductVersionCreate, ProductVersionUpdate, ProductVersionOut,
)
from app.modules.console.services.product_version_service import ProductVersionService

router = APIRouter()


@router.get("")
async def list_versions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取产品版本列表"""
    items, total = await ProductVersionService.get_version_list(db, page, page_size)
    return success(data={
        "list": [ProductVersionOut.model_validate(v).model_dump() for v in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{version_id}")
async def get_version(
    version_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取产品版本详情"""
    version = await ProductVersionService.get_version_by_id(db, version_id)
    if not version:
        return fail("产品版本不存在")
    return success(data=ProductVersionOut.model_validate(version).model_dump())


@router.post("")
async def create_version(
    data: ProductVersionCreate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """创建产品版本"""
    version = await ProductVersionService.create_version(db, data)
    return success(
        data=ProductVersionOut.model_validate(version).model_dump(),
        message="创建成功",
    )


@router.put("/{version_id}")
async def update_version(
    version_id: int,
    data: ProductVersionUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新产品版本"""
    version = await ProductVersionService.update_version(db, version_id, data)
    return success(
        data=ProductVersionOut.model_validate(version).model_dump(),
        message="更新成功",
    )


@router.delete("/{version_id}")
async def delete_version(
    version_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """删除产品版本"""
    await ProductVersionService.delete_version(db, version_id)
    return success(message="删除成功")
