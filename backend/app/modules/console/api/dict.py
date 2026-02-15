"""
数据字典管理接口
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.dict import DictCreate, DictUpdate
from app.modules.console.services.dict_service import DictService

router = APIRouter()


@router.get("/page")
async def page_dicts(
    page: int = Query(1),
    limit: int = Query(20),
    dictCode: Optional[str] = Query(None),
    dictName: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询字典"""
    result = await DictService.page_dicts(db, page, limit, dictCode, dictName)
    return success(data=result)


@router.get("")
async def list_dicts(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询字典列表"""
    items = await DictService.list_dicts(db)
    return success(data=[item.model_dump() for item in items])


@router.post("")
async def add_dict(
    data: DictCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增字典"""
    await DictService.create_dict(db, data)
    await db.commit()
    return success(message="添加成功")


@router.put("")
async def update_dict(
    data: DictUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改字典"""
    await DictService.update_dict(db, data)
    await db.commit()
    return success(message="修改成功")


@router.delete("/{dict_id}")
async def delete_dict(
    dict_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """删除字典"""
    await DictService.delete_dict(db, dict_id)
    await db.commit()
    return success(message="删除成功")
