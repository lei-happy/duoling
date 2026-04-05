"""
地区数据管理服务（租户库）
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.schemas.region.region import (
    RegionCreate, RegionUpdate, RegionOut,
)

# 省级节点的 parent_code 可能是 NULL / '' / '0'（取决于平台数据源）
_ROOT_PARENT_CODES = (None, "", "0")


class RegionService:

    @staticmethod
    def _is_root_parent(parent_code: Optional[str]) -> bool:
        return parent_code in _ROOT_PARENT_CODES

    @staticmethod
    async def _generate_code(db: AsyncSession) -> str:
        """生成自定义地区代码: C + 年月日 + 3位序号"""
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"C{today}"

        result = await db.execute(
            select(BizRegion.code)
            .where(BizRegion.code.like(f"{prefix}%"))
            .order_by(BizRegion.code.desc())
            .limit(1)
        )
        last_code = result.scalar_one_or_none()

        if last_code:
            seq = int(last_code[len(prefix):]) + 1
        else:
            seq = 1

        return f"{prefix}{seq:03d}"

    @staticmethod
    async def _child_count(db: AsyncSession, code: str) -> int:
        result = await db.execute(
            select(func.count()).select_from(BizRegion).where(
                BizRegion.parent_code == code,
                BizRegion.is_deleted == 0,
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_nav_tree(db: AsyncSession) -> List[dict]:
        """获取省+市两级树结构（左侧导航面板用）"""
        result = await db.execute(
            select(BizRegion).where(
                BizRegion.level.in_([1, 2]),
                BizRegion.is_deleted == 0,
            ).order_by(BizRegion.sort_order, BizRegion.code)
        )
        all_rows = result.scalars().all()

        codes = [r.code for r in all_rows]

        count_result = await db.execute(
            select(BizRegion.parent_code, func.count(BizRegion.id)).where(
                BizRegion.parent_code.in_(codes),
                BizRegion.is_deleted == 0,
            ).group_by(BizRegion.parent_code)
        )
        count_map = {row[0]: row[1] for row in count_result.all()}

        node_map: dict = {}
        for r in all_rows:
            node_map[r.code] = {
                "regionId": r.id,
                "code": r.code,
                "name": r.name,
                "parentCode": r.parent_code,
                "level": r.level,
                "childCount": count_map.get(r.code, 0),
                "children": [],
            }

        tree: List[dict] = []
        for r in all_rows:
            node = node_map[r.code]
            if RegionService._is_root_parent(r.parent_code):
                tree.append(node)
            elif r.parent_code in node_map:
                node_map[r.parent_code]["children"].append(node)

        return tree

    @staticmethod
    async def page_children(
        db: AsyncSession,
        parent_code: str,
        page: int = 1,
        limit: int = 20,
        name: Optional[str] = None,
        source: Optional[int] = None,
    ) -> dict:
        """分页查询指定节点的子地区列表（右侧表格用）"""
        base = select(BizRegion).where(
            BizRegion.parent_code == parent_code,
            BizRegion.is_deleted == 0,
        )

        if name:
            base = base.where(BizRegion.name.contains(name))
        if source is not None:
            base = base.where(BizRegion.source == source)

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(BizRegion.sort_order, BizRegion.code)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()

        codes = [r.code for r in rows]
        child_counts: dict[str, int] = {}
        if codes:
            cc_result = await db.execute(
                select(BizRegion.parent_code, func.count(BizRegion.id)).where(
                    BizRegion.parent_code.in_(codes),
                    BizRegion.is_deleted == 0,
                ).group_by(BizRegion.parent_code)
            )
            child_counts = {row[0]: row[1] for row in cc_result.all()}

        items = [
            RegionOut.from_model(r, has_children=child_counts.get(r.code, 0) > 0)
            for r in rows
        ]
        return {
            "list": [item.model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def get_children(
        db: AsyncSession,
        parent_code: Optional[str] = None,
    ) -> List[RegionOut]:
        """获取指定父级的子地区列表（懒加载树用）"""
        if RegionService._is_root_parent(parent_code):
            stmt = select(BizRegion).where(
                or_(
                    BizRegion.parent_code.is_(None),
                    BizRegion.parent_code == "",
                    BizRegion.parent_code == "0",
                ),
                BizRegion.is_deleted == 0,
            )
        else:
            stmt = select(BizRegion).where(
                BizRegion.parent_code == parent_code,
                BizRegion.is_deleted == 0,
            )

        result = await db.execute(
            stmt.order_by(BizRegion.sort_order, BizRegion.code)
        )
        rows = result.scalars().all()

        items: List[RegionOut] = []
        for r in rows:
            child_cnt = await RegionService._child_count(db, r.code)
            items.append(RegionOut.from_model(r, has_children=child_cnt > 0))
        return items

    @staticmethod
    async def search_regions(
        db: AsyncSession,
        name: Optional[str] = None,
        source: Optional[int] = None,
    ) -> List[RegionOut]:
        """按名称搜索地区（扁平列表）"""
        stmt = select(BizRegion).where(BizRegion.is_deleted == 0)

        if name:
            stmt = stmt.where(BizRegion.name.contains(name))
        if source is not None:
            stmt = stmt.where(BizRegion.source == source)

        result = await db.execute(
            stmt.order_by(BizRegion.level, BizRegion.sort_order, BizRegion.code)
            .limit(200)
        )
        return [RegionOut.from_model(r) for r in result.scalars().all()]

    @staticmethod
    async def get_region(db: AsyncSession, region_id: int) -> RegionOut:
        """获取单条地区详情"""
        result = await db.execute(
            select(BizRegion).where(
                BizRegion.id == region_id,
                BizRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException("地区不存在")

        child_cnt = await RegionService._child_count(db, region.code)
        return RegionOut.from_model(region, has_children=child_cnt > 0)

    @staticmethod
    async def create_region(
        db: AsyncSession, data: RegionCreate, user_id: int
    ) -> BizRegion:
        """新增自定义地区"""
        if not data.parentCode:
            raise BizException("自定义地区必须指定上级地区")

        parent_result = await db.execute(
            select(BizRegion).where(
                BizRegion.code == data.parentCode,
                BizRegion.is_deleted == 0,
            )
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise BizException("上级地区不存在")
        if parent.level < 2:
            raise BizException("不允许在省级下直接添加地区，请选择市级节点")
        level = parent.level + 1

        dup_result = await db.execute(
            select(func.count()).select_from(BizRegion).where(
                BizRegion.name == data.name,
                BizRegion.parent_code == data.parentCode,
                BizRegion.is_deleted == 0,
            )
        )
        if (dup_result.scalar() or 0) > 0:
            raise BizException("同一上级下已存在同名地区")

        code = await RegionService._generate_code(db)

        region = BizRegion(
            code=code,
            name=data.name,
            parent_code=data.parentCode,
            level=level,
            sort_order=data.sortOrder,
            status=data.status,
            source=1,
            created_by=user_id,
            longitude=data.longitude,
            latitude=data.latitude,
        )
        db.add(region)
        await db.flush()
        await db.refresh(region)
        return region

    @staticmethod
    async def update_region(
        db: AsyncSession, region_id: int, data: RegionUpdate
    ) -> BizRegion:
        """修改自定义地区（仅 source=1）"""
        result = await db.execute(
            select(BizRegion).where(
                BizRegion.id == region_id,
                BizRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException("地区不存在")
        if region.source != 1:
            raise BizException("系统标准地区不可编辑")

        if data.parentCode is not None and data.parentCode != region.parent_code:
            if data.parentCode:
                parent_result = await db.execute(
                    select(BizRegion).where(
                        BizRegion.code == data.parentCode,
                        BizRegion.is_deleted == 0,
                    )
                )
                parent = parent_result.scalar_one_or_none()
                if not parent:
                    raise BizException("上级地区不存在")
                region.level = parent.level + 1
            else:
                region.level = 1
            region.parent_code = data.parentCode

        if data.name is not None:
            parent_code = data.parentCode if data.parentCode is not None else region.parent_code
            dup_result = await db.execute(
                select(func.count()).select_from(BizRegion).where(
                    BizRegion.name == data.name,
                    BizRegion.parent_code == parent_code,
                    BizRegion.is_deleted == 0,
                    BizRegion.id != region_id,
                )
            )
            if (dup_result.scalar() or 0) > 0:
                raise BizException("同一上级下已存在同名地区")
            region.name = data.name

        if data.sortOrder is not None:
            region.sort_order = data.sortOrder
        if data.status is not None:
            region.status = data.status
        if data.longitude is not None:
            region.longitude = data.longitude
        if data.latitude is not None:
            region.latitude = data.latitude

        await db.flush()
        await db.refresh(region)
        return region

    @staticmethod
    async def delete_region(db: AsyncSession, region_id: int) -> None:
        """软删除自定义地区（仅 source=1）"""
        result = await db.execute(
            select(BizRegion).where(
                BizRegion.id == region_id,
                BizRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException("地区不存在")
        if region.source != 1:
            raise BizException("系统标准地区不可删除")

        children_count = await db.execute(
            select(func.count()).select_from(BizRegion).where(
                BizRegion.parent_code == region.code,
                BizRegion.is_deleted == 0,
            )
        )
        if (children_count.scalar() or 0) > 0:
            raise BizException("请先删除子地区")

        region.is_deleted = 1
        await db.flush()
