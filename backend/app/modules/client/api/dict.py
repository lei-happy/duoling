"""
企业端数据字典管理 API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.dict import (
    BizDictCreate, BizDictUpdate, BizDictOut,
    BizDictItemCreate, BizDictItemUpdate, BizDictItemOut,
)
from app.modules.client.services.dict_service import BizDictService

router = APIRouter()


# ---- 字典 ----

@router.get("")
async def list_dicts(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取字典列表（字段与前端 EleAdmin Dictionary 模型一致）"""
    items = await BizDictService.list_dicts(db)
    return success(
        data=[
            BizDictService.serialize_dictionary_for_frontend(item) for item in items
        ]
    )


@router.post("")
@operation_log(module="数据字典", action="新增", description="新增字典")
async def create_dict(
    request: Request,
    data: BizDictCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建字典"""
    d = await BizDictService.create_dict(db, data)
    return success(data=BizDictOut.from_model(d).model_dump())


@router.put("/{dict_id}")
@operation_log(module="数据字典", action="编辑", description="编辑字典")
async def update_dict(
    request: Request,
    dict_id: int,
    data: BizDictUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新字典"""
    d = await BizDictService.update_dict(db, dict_id, data)
    return success(data=BizDictOut.from_model(d).model_dump())


@router.delete("/{dict_id}")
@operation_log(module="数据字典", action="删除", description="删除字典")
async def delete_dict(
    request: Request,
    dict_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除字典"""
    await BizDictService.delete_dict(db, dict_id)
    return success()


# ---- 字典项 ----

@router.get("/items")
async def list_dict_items(
    dictCode: str = Query(...),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取字典项列表"""
    items = await BizDictService.list_dict_items(db, dictCode)
    return success(data=[item.model_dump() for item in items])


@router.post("/items")
@operation_log(module="数据字典", action="新增", description="新增字典项")
async def create_dict_item(
    request: Request,
    data: BizDictItemCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建字典项"""
    item = await BizDictService.create_dict_item(db, data)
    return success(data=BizDictItemOut.from_model(item).model_dump())


@router.put("/items/{item_id}")
@operation_log(module="数据字典", action="编辑", description="编辑字典项")
async def update_dict_item(
    request: Request,
    item_id: int,
    data: BizDictItemUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新字典项"""
    item = await BizDictService.update_dict_item(db, item_id, data)
    return success(data=BizDictItemOut.from_model(item).model_dump())


@router.delete("/items/{item_id}")
@operation_log(module="数据字典", action="删除", description="删除字典项")
async def delete_dict_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除字典项"""
    await BizDictService.delete_dict_item(db, item_id)
    return success()
