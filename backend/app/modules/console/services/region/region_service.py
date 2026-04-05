"""
Console 端地区数据管理服务（平台库 sys_regions）
所有地区均可编辑，无 source 限制
"""

from typing import Optional, List

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.region.sys_region import SysRegion
from app.modules.console.schemas.region.region import (
    RegionCreate, RegionUpdate, RegionOut,
)

_ROOT_PCODES = (None, 0)


class RegionService:

    @staticmethod
    def _is_root(pcode) -> bool:
        return pcode in _ROOT_PCODES

    @staticmethod
    async def _child_count(db: AsyncSession, code: int) -> int:
        result = await db.execute(
            select(func.count()).select_from(SysRegion).where(
                SysRegion.pcode == code,
                SysRegion.is_deleted == 0,
            )
        )
        return result.scalar() or 0

    # ---- 查询 ----

    @staticmethod
    async def get_nav_tree(db: AsyncSession) -> List[dict]:
        """省+市两级树（左侧导航面板）"""
        result = await db.execute(
            select(SysRegion).where(
                SysRegion.level.in_([1, 2]),
                SysRegion.is_deleted == 0,
            ).order_by(SysRegion.sort_order, SysRegion.code)
        )
        all_rows = result.scalars().all()

        codes = [r.code for r in all_rows]

        count_result = await db.execute(
            select(SysRegion.pcode, func.count(SysRegion.code)).where(
                SysRegion.pcode.in_(codes),
                SysRegion.is_deleted == 0,
            ).group_by(SysRegion.pcode)
        )
        count_map = {row[0]: row[1] for row in count_result.all()}

        node_map: dict = {}
        for r in all_rows:
            node_map[r.code] = {
                "code": r.code,
                "name": r.name,
                "pcode": r.pcode,
                "level": r.level,
                "childCount": count_map.get(r.code, 0),
                "children": [],
            }

        tree: List[dict] = []
        for r in all_rows:
            node = node_map[r.code]
            if RegionService._is_root(r.pcode):
                tree.append(node)
            elif r.pcode in node_map:
                node_map[r.pcode]["children"].append(node)

        return tree

    @staticmethod
    async def page_children(
        db: AsyncSession,
        pcode: int,
        page: int = 1,
        limit: int = 20,
        name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        """分页查询指定节点的子地区（右侧表格）"""
        base = select(SysRegion).where(
            SysRegion.pcode == pcode,
            SysRegion.is_deleted == 0,
        )

        if name:
            base = base.where(SysRegion.name.contains(name))
        if status is not None:
            base = base.where(SysRegion.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(SysRegion.sort_order, SysRegion.code)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()

        codes = [r.code for r in rows]
        child_counts: dict[int, int] = {}
        if codes:
            cc_result = await db.execute(
                select(SysRegion.pcode, func.count(SysRegion.code)).where(
                    SysRegion.pcode.in_(codes),
                    SysRegion.is_deleted == 0,
                ).group_by(SysRegion.pcode)
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
        pcode: Optional[int] = None,
    ) -> List[RegionOut]:
        """获取子地区列表（懒加载树）"""
        if RegionService._is_root(pcode):
            stmt = select(SysRegion).where(
                or_(
                    SysRegion.pcode.is_(None),
                    SysRegion.pcode == 0,
                ),
                SysRegion.is_deleted == 0,
            )
        else:
            stmt = select(SysRegion).where(
                SysRegion.pcode == pcode,
                SysRegion.is_deleted == 0,
            )

        result = await db.execute(
            stmt.order_by(SysRegion.sort_order, SysRegion.code)
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
        status: Optional[int] = None,
    ) -> List[RegionOut]:
        """按名称搜索地区（扁平列表）"""
        stmt = select(SysRegion).where(SysRegion.is_deleted == 0)

        if name:
            stmt = stmt.where(SysRegion.name.contains(name))
        if status is not None:
            stmt = stmt.where(SysRegion.status == status)

        result = await db.execute(
            stmt.order_by(SysRegion.level, SysRegion.sort_order, SysRegion.code)
            .limit(200)
        )
        return [RegionOut.from_model(r) for r in result.scalars().all()]

    @staticmethod
    async def get_region(db: AsyncSession, code: int) -> RegionOut:
        """获取单条地区详情"""
        result = await db.execute(
            select(SysRegion).where(
                SysRegion.code == code,
                SysRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException("地区不存在")

        child_cnt = await RegionService._child_count(db, region.code)
        return RegionOut.from_model(region, has_children=child_cnt > 0)

    # ---- 写操作 ----

    @staticmethod
    async def create_region(
        db: AsyncSession, data: RegionCreate
    ) -> SysRegion:
        """新增地区"""
        if data.pcode is None:
            raise BizException("必须指定上级地区")

        parent_result = await db.execute(
            select(SysRegion).where(
                SysRegion.code == data.pcode,
                SysRegion.is_deleted == 0,
            )
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise BizException("上级地区不存在")

        level = parent.level + 1

        dup_result = await db.execute(
            select(func.count()).select_from(SysRegion).where(
                SysRegion.name == data.name,
                SysRegion.pcode == data.pcode,
                SysRegion.is_deleted == 0,
            )
        )
        if (dup_result.scalar() or 0) > 0:
            raise BizException("同一上级下已存在同名地区")

        code = await RegionService._generate_code(db, data.pcode)

        region = SysRegion(
            code=code,
            name=data.name,
            short_name=data.shortName,
            pcode=data.pcode,
            level=level,
            sort_order=data.sortOrder,
            status=data.status,
        )
        db.add(region)
        await db.flush()
        return region

    @staticmethod
    async def _generate_code(db: AsyncSession, pcode: int) -> int:
        """
        在父级 code 下生成新的子代码。
        规则：取父级下已有最大 code + 1；无子级时 pcode * 100 + 1（仅作为兜底）。
        """
        result = await db.execute(
            select(func.max(SysRegion.code)).where(
                SysRegion.pcode == pcode,
            )
        )
        max_code = result.scalar_one_or_none()
        if max_code:
            return max_code + 1
        return pcode * 100 + 1

    @staticmethod
    async def update_region(
        db: AsyncSession, code: int, data: RegionUpdate
    ) -> SysRegion:
        """编辑地区"""
        result = await db.execute(
            select(SysRegion).where(
                SysRegion.code == code,
                SysRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException("地区不存在")

        if data.name is not None and data.name != region.name:
            dup_result = await db.execute(
                select(func.count()).select_from(SysRegion).where(
                    SysRegion.name == data.name,
                    SysRegion.pcode == region.pcode,
                    SysRegion.is_deleted == 0,
                    SysRegion.code != code,
                )
            )
            if (dup_result.scalar() or 0) > 0:
                raise BizException("同一上级下已存在同名地区")
            region.name = data.name

        if data.shortName is not None:
            region.short_name = data.shortName
        if data.sortOrder is not None:
            region.sort_order = data.sortOrder
        if data.status is not None:
            region.status = data.status

        await db.flush()
        return region

    @staticmethod
    async def delete_region(db: AsyncSession, code: int) -> None:
        """软删除地区"""
        result = await db.execute(
            select(SysRegion).where(
                SysRegion.code == code,
                SysRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException("地区不存在")

        children_count = await db.execute(
            select(func.count()).select_from(SysRegion).where(
                SysRegion.pcode == region.code,
                SysRegion.is_deleted == 0,
            )
        )
        if (children_count.scalar() or 0) > 0:
            raise BizException("请先删除子地区")

        region.is_deleted = 1
        await db.flush()
