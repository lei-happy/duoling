"""
字典数据管理服务
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.dictionary.dict_model import Dict, DictItem
from app.modules.console.schemas.dictionary.dict import DictDataOut, DictDataCreate, DictDataUpdate


class DictDataService:
    """字典数据管理服务"""

    @staticmethod
    def _to_out(item: DictItem) -> DictDataOut:
        """将 ORM 模型转换为输出"""
        return DictDataOut(
            dictDataId=item.id,
            dictId=item.dict_id,
            dictCode=item.dict_code,
            dictDataCode=item.item_value,
            dictDataName=item.item_name,
            sortNumber=item.sort_order,
            comments=item.remark,
            createTime=item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None,
        )

    @staticmethod
    async def list_dict_data(
        db: AsyncSession,
        dictCode: Optional[str] = None,
        dictId: Optional[int] = None,
    ) -> List[DictDataOut]:
        """查询字典数据列表（不分页），供 DictData 组件使用"""
        query = select(DictItem).where(DictItem.is_deleted == 0)
        if dictCode:
            query = query.where(DictItem.dict_code == dictCode)
        if dictId is not None:
            query = query.where(DictItem.dict_id == dictId)
        query = query.order_by(DictItem.sort_order, DictItem.id)
        result = await db.execute(query)
        items = result.scalars().all()
        return [DictDataService._to_out(item) for item in items]

    @staticmethod
    async def page_dict_data(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        dictId: Optional[int] = None,
        dictDataName: Optional[str] = None,
        dictDataCode: Optional[str] = None,
    ) -> dict:
        """分页查询字典数据"""
        query = select(DictItem).where(DictItem.is_deleted == 0)
        if dictId is not None:
            query = query.where(DictItem.dict_id == dictId)
        if dictDataName:
            query = query.where(DictItem.item_name.contains(dictDataName))
        if dictDataCode:
            query = query.where(DictItem.item_value.contains(dictDataCode))

        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        query = query.order_by(DictItem.sort_order, DictItem.id)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return {
            "list": [DictDataService._to_out(item).model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def create_dict_data(db: AsyncSession, data: DictDataCreate) -> None:
        """新增字典数据项"""
        # 查询关联的字典，获取 dict_code
        dict_result = await db.execute(
            select(Dict).where(Dict.id == data.dictId, Dict.is_deleted == 0)
        )
        d = dict_result.scalar_one_or_none()
        if not d:
            raise BizException("关联的字典不存在")

        item = DictItem(
            dict_id=data.dictId,
            dict_code=d.dict_code,
            item_name=data.dictDataName,
            item_value=data.dictDataCode,
            sort_order=data.sortNumber,
            remark=data.comments,
        )
        db.add(item)
        await db.flush()

    @staticmethod
    async def update_dict_data(db: AsyncSession, data: DictDataUpdate) -> None:
        """修改字典数据项"""
        result = await db.execute(
            select(DictItem).where(DictItem.id == data.dictDataId, DictItem.is_deleted == 0)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise BizException("字典数据不存在")

        if data.dictDataName is not None:
            item.item_name = data.dictDataName
        if data.dictDataCode is not None:
            item.item_value = data.dictDataCode
        if data.sortNumber is not None:
            item.sort_order = data.sortNumber
        if data.comments is not None:
            item.remark = data.comments

        await db.flush()

    @staticmethod
    async def delete_dict_data(db: AsyncSession, dict_data_id: int) -> None:
        """删除单条字典数据（软删除）"""
        result = await db.execute(
            select(DictItem).where(DictItem.id == dict_data_id, DictItem.is_deleted == 0)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise BizException("字典数据不存在")
        item.is_deleted = 1
        await db.flush()

    @staticmethod
    async def batch_delete_dict_data(db: AsyncSession, ids: List[int]) -> None:
        """批量删除字典数据（软删除）"""
        result = await db.execute(
            select(DictItem).where(DictItem.id.in_(ids), DictItem.is_deleted == 0)
        )
        items = result.scalars().all()
        for item in items:
            item.is_deleted = 1
        await db.flush()
