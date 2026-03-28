"""
企业端字典数据接口（供 DictData 组件使用）
路由前缀: /system/dictionary-data
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.models.biz_dict import BizDictItem

from sqlalchemy import select

router = APIRouter()


@router.get("")
async def list_dict_data(
    dictCode: Optional[str] = Query(None),
    dictId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """查询字典数据列表（供 DictData 组件使用）"""
    query = select(BizDictItem).where(BizDictItem.is_deleted == 0)
    if dictCode:
        query = query.where(BizDictItem.dict_code == dictCode)
    if dictId is not None:
        query = query.where(BizDictItem.dict_id == dictId)
    query = query.order_by(BizDictItem.sort_order, BizDictItem.id)
    result = await db.execute(query)
    items = result.scalars().all()

    return success(data=[
        {
            "dictDataId": item.id,
            "dictId": item.dict_id,
            "dictCode": item.dict_code,
            "dictDataCode": item.item_value,
            "dictDataName": item.item_name,
            "sortNumber": item.sort_order,
            "comments": item.remark,
            "createTime": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None,
        }
        for item in items
    ])
