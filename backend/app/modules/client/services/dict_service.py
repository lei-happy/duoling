"""
企业端数据字典管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.biz_dict import BizDict, BizDictItem
from app.modules.client.schemas.dict import (
    BizDictCreate, BizDictUpdate, BizDictOut,
    BizDictItemCreate, BizDictItemUpdate, BizDictItemOut,
)

# 与前端表格列 prop 对齐，仅允许白名单字段参与排序
_DICT_ITEM_SORT_COLUMNS = {
    "dictDataName": BizDictItem.item_name,
    "dictDataCode": BizDictItem.item_value,
    "sortNumber": BizDictItem.sort_order,
    "createTime": BizDictItem.created_at,
}


def _dict_item_order_clauses(sort: Optional[str], order: Optional[str]):
    col = _DICT_ITEM_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [asc(BizDictItem.sort_order), desc(BizDictItem.id)]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    if col is BizDictItem.created_at:
        return [primary, desc(BizDictItem.id)]
    return [primary, desc(BizDictItem.id)]


class BizDictService:

    # ---- 前端 EleAdmin 字段序列化 ----

    @staticmethod
    def serialize_dictionary_for_frontend(item: BizDictOut) -> dict:
        """字典列表/树：与前端 Dictionary 模型字段一致。"""
        return {
            "dictId": item.id,
            "dictCode": item.dictCode,
            "dictName": item.dictName,
            "sortNumber": item.sortOrder,
            "comments": item.remark or "",
            "createTime": item.createdAt.strftime("%Y-%m-%d %H:%M:%S")
            if item.createdAt
            else None,
        }

    @staticmethod
    def serialize_dict_item_row(item: BizDictItem) -> dict:
        """字典数据行：与 GET /dictionary-data 及分页列表一致。"""
        return {
            "dictDataId": item.id,
            "dictId": item.dict_id,
            "dictCode": item.dict_code,
            "dictDataCode": item.item_value,
            "dictDataName": item.item_name,
            "sortNumber": item.sort_order,
            "comments": item.remark,
            "createTime": item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if item.created_at
            else None,
        }

    @staticmethod
    async def get_dict_code_by_id(
        db: AsyncSession, dict_id: int
    ) -> Optional[str]:
        result = await db.execute(
            select(BizDict.dict_code).where(
                BizDict.id == dict_id,
                BizDict.is_deleted == 0,
            )
        )
        return result.scalar_one_or_none()

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
        await db.refresh(d)
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
        await db.refresh(d)
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

    @staticmethod
    async def page_dict_items(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        dict_id: Optional[int] = None,
        dict_data_name: Optional[str] = None,
        dict_data_code: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        """分页查询字典项（前端 dictionary-data 表格）。"""
        base = select(BizDictItem).where(BizDictItem.is_deleted == 0)
        if dict_id is not None:
            base = base.where(BizDictItem.dict_id == dict_id)
        if dict_data_name:
            base = base.where(BizDictItem.item_name.contains(dict_data_name))
        if dict_data_code:
            base = base.where(BizDictItem.item_value.contains(dict_data_code))

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(*_dict_item_order_clauses(sort, order))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "list": [BizDictService.serialize_dict_item_row(r) for r in rows],
            "count": count,
        }

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
        await db.refresh(item)
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
        await db.refresh(item)
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
