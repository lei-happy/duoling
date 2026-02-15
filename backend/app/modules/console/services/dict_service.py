"""
数据字典管理服务
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.dict import Dict, DictItem
from app.modules.console.schemas.dict import DictOut, DictCreate, DictUpdate


class DictService:
    """数据字典管理服务"""

    @staticmethod
    def _to_out(d: Dict) -> DictOut:
        """将 ORM 模型转换为输出"""
        return DictOut(
            dictId=d.id,
            dictCode=d.dict_code,
            dictName=d.dict_name,
            sortNumber=d.sort_order,
            comments=d.remark,
            createTime=d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else None,
        )

    @staticmethod
    async def list_dicts(db: AsyncSession) -> List[DictOut]:
        """查询字典列表（不分页）"""
        query = (
            select(Dict)
            .where(Dict.is_deleted == 0)
            .order_by(Dict.sort_order, Dict.id)
        )
        result = await db.execute(query)
        items = result.scalars().all()
        return [DictService._to_out(d) for d in items]

    @staticmethod
    async def page_dicts(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        dictCode: Optional[str] = None,
        dictName: Optional[str] = None,
    ) -> dict:
        """分页查询字典"""
        query = select(Dict).where(Dict.is_deleted == 0)
        if dictCode:
            query = query.where(Dict.dict_code.contains(dictCode))
        if dictName:
            query = query.where(Dict.dict_name.contains(dictName))

        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        query = query.order_by(Dict.sort_order, Dict.id)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return {
            "list": [DictService._to_out(d).model_dump() for d in items],
            "count": count,
        }

    @staticmethod
    async def create_dict(db: AsyncSession, data: DictCreate) -> None:
        """新增字典"""
        # 检查字典编码唯一性
        existing = await db.execute(
            select(Dict).where(Dict.dict_code == data.dictCode, Dict.is_deleted == 0)
        )
        if existing.scalar_one_or_none():
            raise BizException("字典编码已存在")

        d = Dict(
            dict_code=data.dictCode,
            dict_name=data.dictName,
            sort_order=data.sortNumber,
            remark=data.comments,
        )
        db.add(d)
        await db.flush()

    @staticmethod
    async def update_dict(db: AsyncSession, data: DictUpdate) -> None:
        """修改字典"""
        result = await db.execute(
            select(Dict).where(Dict.id == data.dictId, Dict.is_deleted == 0)
        )
        d = result.scalar_one_or_none()
        if not d:
            raise BizException("字典不存在")

        if data.dictCode is not None:
            # 检查字典编码唯一性
            dup = await db.execute(
                select(Dict).where(
                    Dict.dict_code == data.dictCode,
                    Dict.id != data.dictId,
                    Dict.is_deleted == 0,
                )
            )
            if dup.scalar_one_or_none():
                raise BizException("字典编码已存在")
            d.dict_code = data.dictCode
        if data.dictName is not None:
            d.dict_name = data.dictName
        if data.sortNumber is not None:
            d.sort_order = data.sortNumber
        if data.comments is not None:
            d.remark = data.comments

        await db.flush()

    @staticmethod
    async def delete_dict(db: AsyncSession, dict_id: int) -> None:
        """删除字典及其下所有字典数据项（软删除）"""
        result = await db.execute(
            select(Dict).where(Dict.id == dict_id, Dict.is_deleted == 0)
        )
        d = result.scalar_one_or_none()
        if not d:
            raise BizException("字典不存在")

        # 软删除字典
        d.is_deleted = 1

        # 软删除该字典下的所有数据项
        items_result = await db.execute(
            select(DictItem).where(DictItem.dict_id == dict_id, DictItem.is_deleted == 0)
        )
        items = items_result.scalars().all()
        for item in items:
            item.is_deleted = 1

        await db.flush()
