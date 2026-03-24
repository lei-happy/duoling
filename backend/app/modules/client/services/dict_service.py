"""
企业端数据字典管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.biz_dict import BizDict, BizDictItem
from app.modules.client.schemas.dict import (
    BizDictCreate, BizDictUpdate, BizDictOut,
    BizDictItemCreate, BizDictItemUpdate, BizDictItemOut,
)


class BizDictService:

    # ---- 字典 CRUD ----

    @staticmethod
    async def list_dicts(db: AsyncSession) -> List[BizDictOut]:
        result = await db.execute(
            select(BizDict)
            .where(BizDict.is_deleted == 0)
            .order_by(BizDict.sort_order, BizDict.id)
        )
        return [BizDictOut.from_model(d) for d in result.scalars().all()]

    @staticmethod
    async def create_dict(db: AsyncSession, data: BizDictCreate) -> BizDict:
        existing = await db.execute(
            select(BizDict).where(
                BizDict.dict_code == data.dictCode,
                BizDict.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"字典编码 {data.dictCode} 已存在")

        d = BizDict(
            dict_code=data.dictCode,
            dict_name=data.dictName,
            sort_order=data.sortOrder,
            remark=data.remark,
        )
        db.add(d)
        await db.flush()
        return d

    @staticmethod
    async def update_dict(
        db: AsyncSession, dict_id: int, data: BizDictUpdate
    ) -> BizDict:
        result = await db.execute(
            select(BizDict).where(
                BizDict.id == dict_id,
                BizDict.is_deleted == 0,
            )
        )
        d = result.scalar_one_or_none()
        if not d:
            raise BizException("字典不存在")

        field_map = {
            "dictName": "dict_name",
            "sortOrder": "sort_order",
            "status": "status",
            "remark": "remark",
        }
        for sf, mf in field_map.items():
            val = getattr(data, sf, None)
            if val is not None:
                setattr(d, mf, val)

        await db.flush()
        return d

    @staticmethod
    async def delete_dict(db: AsyncSession, dict_id: int) -> None:
        result = await db.execute(
            select(BizDict).where(
                BizDict.id == dict_id,
                BizDict.is_deleted == 0,
            )
        )
        d = result.scalar_one_or_none()
        if not d:
            raise BizException("字典不存在")
        d.is_deleted = 1
        await db.flush()

    # ---- 字典项 CRUD ----

    @staticmethod
    async def list_dict_items(
        db: AsyncSession, dict_code: str
    ) -> List[BizDictItemOut]:
        result = await db.execute(
            select(BizDictItem)
            .where(
                BizDictItem.dict_code == dict_code,
                BizDictItem.is_deleted == 0,
            )
            .order_by(BizDictItem.sort_order, BizDictItem.id)
        )
        return [BizDictItemOut.from_model(i) for i in result.scalars().all()]

    @staticmethod
    async def create_dict_item(
        db: AsyncSession, data: BizDictItemCreate
    ) -> BizDictItem:
        item = BizDictItem(
            dict_id=data.dictId,
            dict_code=data.dictCode,
            item_name=data.itemName,
            item_value=data.itemValue,
            sort_order=data.sortOrder,
            remark=data.remark,
        )
        db.add(item)
        await db.flush()
        return item

    @staticmethod
    async def update_dict_item(
        db: AsyncSession, item_id: int, data: BizDictItemUpdate
    ) -> BizDictItem:
        result = await db.execute(
            select(BizDictItem).where(
                BizDictItem.id == item_id,
                BizDictItem.is_deleted == 0,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise BizException("字典项不存在")

        field_map = {
            "itemName": "item_name",
            "itemValue": "item_value",
            "sortOrder": "sort_order",
            "status": "status",
            "remark": "remark",
        }
        for sf, mf in field_map.items():
            val = getattr(data, sf, None)
            if val is not None:
                setattr(item, mf, val)

        await db.flush()
        return item

    @staticmethod
    async def delete_dict_item(db: AsyncSession, item_id: int) -> None:
        result = await db.execute(
            select(BizDictItem).where(
                BizDictItem.id == item_id,
                BizDictItem.is_deleted == 0,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise BizException("字典项不存在")
        item.is_deleted = 1
        await db.flush()
