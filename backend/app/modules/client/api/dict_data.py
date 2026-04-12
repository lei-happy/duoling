"""
企业端字典数据接口（与前端 EleAdmin /dictionary-data 契约一致）
路由前缀: /system/dictionary-data
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.common.exceptions import BizException
from app.modules.client.models.biz_dict import BizDictItem
from app.modules.client.schemas.dict import (
    BizDictItemCreate,
    BizDictItemUpdate,
    BizDictItemApiCreate,
    BizDictItemApiUpdate,
)
from app.modules.client.services.dict_service import BizDictService

router = APIRouter()


@router.get("/page")
async def page_dict_data(
    page: int = Query(1),
    limit: int = Query(20),
    dictId: Optional[int] = Query(None),
    dictDataName: Optional[str] = Query(None),
    dictDataCode: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询字典数据"""
    result = await BizDictService.page_dict_items(
        db,
        page=page,
        limit=limit,
        dict_id=dictId,
        dict_data_name=dictDataName,
        dict_data_code=dictDataCode,
        sort=sort,
        order=order,
    )
    return success(data=result)


@router.get("")
async def list_dict_data(
    dictCode: Optional[str] = Query(None),
    dictId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """查询字典数据列表（供 DictData 组件、字典缓存使用）"""
    query = select(BizDictItem).where(BizDictItem.is_deleted == 0)
    if dictCode:
        query = query.where(BizDictItem.dict_code == dictCode)
    if dictId is not None:
        query = query.where(BizDictItem.dict_id == dictId)
    query = query.order_by(BizDictItem.sort_order, BizDictItem.id)
    result = await db.execute(query)
    items = result.scalars().all()

    return success(
        data=[BizDictService.serialize_dict_item_row(item) for item in items]
    )


@router.post("")
@operation_log(module="数据字典", action="新增", description="新增字典数据")
async def add_dict_data(
    request: Request,
    data: BizDictItemApiCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """新增字典数据"""
    dict_code = data.dictCode
    if not dict_code:
        dict_code = await BizDictService.get_dict_code_by_id(db, data.dictId)
    if not dict_code:
        raise BizException("字典不存在或缺少字典编码")

    item_value = data.dictDataCode
    if not item_value:
        item_value = uuid.uuid4().hex[:8]

    sort_order = data.sortNumber
    if sort_order is None:
        result = await db.execute(
            select(func.max(BizDictItem.sort_order)).where(
                BizDictItem.dict_id == data.dictId,
                BizDictItem.is_deleted == 0,
            )
        )
        max_sort = result.scalar() or 0
        sort_order = max_sort + 10

    create = BizDictItemCreate(
        dictId=data.dictId,
        dictCode=dict_code,
        itemName=data.dictDataName,
        itemValue=item_value,
        sortOrder=sort_order,
        remark=data.comments,
    )
    item = await BizDictService.create_dict_item(db, create)
    return success(data=BizDictService.serialize_dict_item_row(item))


@router.put("")
@operation_log(module="数据字典", action="编辑", description="编辑字典数据")
async def update_dict_data(
    request: Request,
    data: BizDictItemApiUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """修改字典数据"""
    if not data.dictDataId:
        raise BizException("缺少字典数据 ID")
    update = BizDictItemUpdate(
        itemName=data.dictDataName,
        itemValue=data.dictDataCode,
        sortOrder=data.sortNumber,
        remark=data.comments,
    )
    item = await BizDictService.update_dict_item(db, data.dictDataId, update)
    return success(data=BizDictService.serialize_dict_item_row(item))


@router.delete("/batch")
@operation_log(module="数据字典", action="批量删除", description="批量删除字典数据")
async def batch_delete_dict_data(
    request: Request,
    data: List[int] = Body(...),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """批量删除字典数据"""
    for item_id in data:
        if item_id is not None:
            await BizDictService.delete_dict_item(db, item_id)
    return success()


@router.delete("/{item_id}")
@operation_log(module="数据字典", action="删除", description="删除字典数据")
async def delete_dict_data(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除单条字典数据"""
    await BizDictService.delete_dict_item(db, item_id)
    return success()
