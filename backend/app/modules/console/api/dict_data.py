"""
字典数据管理接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.dict import DictDataCreate, DictDataUpdate
from app.modules.console.services.dict_data_service import DictDataService

router = APIRouter()


@router.get("/page")
async def page_dict_data(
    page: int = Query(1),
    limit: int = Query(20),
    dictId: Optional[int] = Query(None),
    dictDataName: Optional[str] = Query(None),
    dictDataCode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询字典数据"""
    result = await DictDataService.page_dict_data(
        db, page, limit, dictId, dictDataName, dictDataCode
    )
    return success(data=result)


@router.get("")
async def list_dict_data(
    dictCode: Optional[str] = Query(None),
    dictId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询字典数据列表（供 DictData 组件使用）"""
    items = await DictDataService.list_dict_data(db, dictCode, dictId)
    return success(data=[item.model_dump() for item in items])


@router.post("")
async def add_dict_data(
    data: DictDataCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增字典数据"""
    await DictDataService.create_dict_data(db, data)
    await db.commit()
    return success(message="添加成功")


@router.put("")
async def update_dict_data(
    data: DictDataUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改字典数据"""
    await DictDataService.update_dict_data(db, data)
    await db.commit()
    return success(message="修改成功")


@router.delete("/batch")
async def batch_delete_dict_data(
    ids: List[int] = Body(..., embed=False),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量删除字典数据"""
    await DictDataService.batch_delete_dict_data(db, ids)
    await db.commit()
    return success(message="删除成功")


@router.delete("/{dict_data_id}")
async def delete_dict_data(
    dict_data_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """删除字典数据"""
    await DictDataService.delete_dict_data(db, dict_data_id)
    await db.commit()
    return success(message="删除成功")
