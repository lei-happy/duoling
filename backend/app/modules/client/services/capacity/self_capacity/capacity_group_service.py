"""
运力分组服务（租户库）

分组 CRUD、成员增删、分组成员分页；并对外提供「司机所属分组ID集合」查询，
供计费成本引擎的 capacity_group 条件按需预加载。
"""

from typing import Optional

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.capacity_group import (
    CapacityGroup,
    CapacityGroupMember,
)
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.schemas.capacity.self_capacity.capacity_group import (
    CapacityGroupCreate,
    CapacityGroupUpdate,
    CapacityGroupOut,
    CapacityGroupOption,
    CapacityGroupMemberOut,
)


class CapacityGroupService:

    # ---------------- 分组 ----------------

    @staticmethod
    async def _member_count_map(
        db: AsyncSession, group_ids: list[int]
    ) -> dict[int, int]:
        if not group_ids:
            return {}
        result = await db.execute(
            select(
                CapacityGroupMember.group_id,
                func.count(CapacityGroupMember.id),
            )
            .where(
                CapacityGroupMember.group_id.in_(group_ids),
                CapacityGroupMember.is_deleted == 0,
            )
            .group_by(CapacityGroupMember.group_id)
        )
        return {int(gid): int(cnt) for gid, cnt in result.all()}

    @staticmethod
    async def page_groups(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        enterprise_id: Optional[int] = None,
    ) -> dict:
        base = select(CapacityGroup).where(CapacityGroup.is_deleted == 0)
        if keyword:
            kw = f"%{keyword}%"
            base = base.where(
                or_(
                    CapacityGroup.group_name.like(kw),
                    CapacityGroup.group_code.like(kw),
                )
            )
        if status is not None:
            base = base.where(CapacityGroup.status == status)
        if enterprise_id is not None:
            base = base.where(CapacityGroup.enterprise_id == enterprise_id)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(
                CapacityGroup.sort_order.asc(), CapacityGroup.id.desc()
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        groups = result.scalars().all()
        count_map = await CapacityGroupService._member_count_map(
            db, [g.id for g in groups]
        )

        return {
            "list": [
                CapacityGroupOut.from_model(
                    g, member_count=count_map.get(g.id, 0)
                ).model_dump()
                for g in groups
            ],
            "total": total,
            "count": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_options(
        db: AsyncSession, enterprise_id: Optional[int] = None
    ) -> list[dict]:
        base = select(CapacityGroup).where(
            CapacityGroup.is_deleted == 0,
            CapacityGroup.status == 1,
        )
        if enterprise_id is not None:
            base = base.where(CapacityGroup.enterprise_id == enterprise_id)
        result = await db.execute(
            base.order_by(CapacityGroup.sort_order.asc(), CapacityGroup.id.desc())
        )
        return [
            CapacityGroupOption(
                id=g.id, groupName=g.group_name,
                groupCode=g.group_code, color=g.color,
            ).model_dump()
            for g in result.scalars().all()
        ]

    @staticmethod
    async def _get_group(db: AsyncSession, group_id: int) -> CapacityGroup:
        result = await db.execute(
            select(CapacityGroup).where(
                CapacityGroup.id == group_id,
                CapacityGroup.is_deleted == 0,
            )
        )
        group = result.scalar_one_or_none()
        if not group:
            raise BizException("运力分组不存在")
        return group

    @staticmethod
    async def _assert_name_unique(
        db: AsyncSession,
        name: str,
        enterprise_id: Optional[int],
        exclude_id: Optional[int] = None,
    ) -> None:
        q = select(CapacityGroup.id).where(
            CapacityGroup.group_name == name,
            CapacityGroup.is_deleted == 0,
        )
        if enterprise_id is None:
            q = q.where(CapacityGroup.enterprise_id.is_(None))
        else:
            q = q.where(CapacityGroup.enterprise_id == enterprise_id)
        if exclude_id is not None:
            q = q.where(CapacityGroup.id != exclude_id)
        if (await db.execute(q)).first():
            raise BizException(f"分组名称「{name}」已存在，请换一个")

    @staticmethod
    async def _assert_code_unique(
        db: AsyncSession, code: str, exclude_id: Optional[int] = None
    ) -> None:
        q = select(CapacityGroup.id).where(
            CapacityGroup.group_code == code,
            CapacityGroup.is_deleted == 0,
        )
        if exclude_id is not None:
            q = q.where(CapacityGroup.id != exclude_id)
        if (await db.execute(q)).first():
            raise BizException(f"分组编码「{code}」已被占用，请换一个")

    @staticmethod
    async def create_group(
        db: AsyncSession,
        data: CapacityGroupCreate,
        operator_user_id: Optional[int] = None,
    ) -> CapacityGroupOut:
        name = (data.groupName or "").strip()
        if not name:
            raise BizException("请填写分组名称")
        await CapacityGroupService._assert_name_unique(
            db, name, data.enterpriseId
        )
        code = (data.groupCode or "").strip() or None
        if code:
            await CapacityGroupService._assert_code_unique(db, code)

        group = CapacityGroup(
            enterprise_id=data.enterpriseId,
            group_name=name,
            group_code=code,
            color=data.color,
            sort_order=data.sortOrder or 0,
            status=data.status if data.status is not None else 1,
            remark=data.remark,
            created_by=operator_user_id,
            updated_by=operator_user_id,
        )
        db.add(group)
        await db.flush()

        if not group.group_code:
            group.group_code = f"CG{group.id:04d}"
            await db.flush()

        await db.refresh(group)
        return CapacityGroupOut.from_model(group, member_count=0)

    @staticmethod
    async def update_group(
        db: AsyncSession,
        group_id: int,
        data: CapacityGroupUpdate,
        operator_user_id: Optional[int] = None,
    ) -> CapacityGroupOut:
        group = await CapacityGroupService._get_group(db, group_id)

        if data.groupName is not None:
            name = data.groupName.strip()
            if not name:
                raise BizException("请填写分组名称")
            await CapacityGroupService._assert_name_unique(
                db, name, group.enterprise_id, exclude_id=group_id
            )
            group.group_name = name
        if data.groupCode is not None:
            code = data.groupCode.strip() or None
            if code:
                await CapacityGroupService._assert_code_unique(
                    db, code, exclude_id=group_id
                )
            group.group_code = code
        if data.color is not None:
            group.color = data.color
        if data.sortOrder is not None:
            group.sort_order = data.sortOrder
        if data.status is not None:
            group.status = data.status
        if data.remark is not None:
            group.remark = data.remark
        group.updated_by = operator_user_id
        await db.flush()
        await db.refresh(group)

        count_map = await CapacityGroupService._member_count_map(db, [group.id])
        return CapacityGroupOut.from_model(
            group, member_count=count_map.get(group.id, 0)
        )

    @staticmethod
    async def update_status(
        db: AsyncSession, group_id: int, status: int
    ) -> None:
        if status not in (0, 1):
            raise BizException("状态取值不合法")
        group = await CapacityGroupService._get_group(db, group_id)
        group.status = status
        await db.flush()

    @staticmethod
    async def delete_group(db: AsyncSession, group_id: int) -> None:
        group = await CapacityGroupService._get_group(db, group_id)
        group.is_deleted = 1
        members = await db.execute(
            select(CapacityGroupMember).where(
                CapacityGroupMember.group_id == group_id,
                CapacityGroupMember.is_deleted == 0,
            )
        )
        for m in members.scalars().all():
            m.is_deleted = 1
        await db.flush()

    # ---------------- 成员 ----------------

    @staticmethod
    async def page_members(
        db: AsyncSession,
        group_id: int,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
    ) -> dict:
        await CapacityGroupService._get_group(db, group_id)

        # 关联当前绑定中的运力（同一司机取绑定中的一条），联查手机号
        current_cap = (
            select(
                Capacity.driver_id.label("cap_driver_id"),
                func.max(Capacity.id).label("cap_id"),
                func.max(Capacity.plate_number).label("cap_plate"),
            )
            .where(Capacity.status == 1, Capacity.is_deleted == 0)
            .group_by(Capacity.driver_id)
            .subquery()
        )

        base = (
            select(
                CapacityGroupMember,
                Driver.phone,
                current_cap.c.cap_id,
                current_cap.c.cap_plate,
            )
            .outerjoin(
                Driver,
                and_(
                    Driver.id == CapacityGroupMember.driver_id,
                    Driver.is_deleted == 0,
                ),
            )
            .outerjoin(
                current_cap,
                current_cap.c.cap_driver_id == CapacityGroupMember.driver_id,
            )
            .where(
                CapacityGroupMember.group_id == group_id,
                CapacityGroupMember.is_deleted == 0,
            )
        )
        if keyword:
            kw = f"%{keyword}%"
            base = base.where(
                or_(
                    CapacityGroupMember.driver_name.like(kw),
                    CapacityGroupMember.plate_number.like(kw),
                    Driver.phone.like(kw),
                )
            )

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(CapacityGroupMember.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()

        return {
            "list": [
                CapacityGroupMemberOut.from_model(
                    m,
                    driver_phone=phone,
                    current_capacity_id=cap_id,
                    current_plate=cap_plate,
                ).model_dump()
                for m, phone, cap_id, cap_plate in rows
            ],
            "total": total,
            "count": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def add_members(
        db: AsyncSession,
        group_id: int,
        capacity_ids: list[int],
        operator_user_id: Optional[int] = None,
    ) -> dict:
        await CapacityGroupService._get_group(db, group_id)
        if not capacity_ids:
            raise BizException("请选择要加入分组的运力")

        # 由运力ID解析出司机（成员锚点）
        cap_rows = await db.execute(
            select(
                Capacity.id, Capacity.driver_id,
                Capacity.driver_name, Capacity.plate_number,
            ).where(
                Capacity.id.in_(capacity_ids),
                Capacity.is_deleted == 0,
            )
        )
        cap_map = {
            r.id: (r.driver_id, r.driver_name, r.plate_number)
            for r in cap_rows.all()
        }

        # 已在本组的司机（未删除）
        existing = await db.execute(
            select(CapacityGroupMember.driver_id).where(
                CapacityGroupMember.group_id == group_id,
                CapacityGroupMember.is_deleted == 0,
            )
        )
        existing_drivers = {int(d) for (d,) in existing.all()}

        added, skipped = 0, 0
        seen_drivers: set[int] = set()
        for cid in capacity_ids:
            info = cap_map.get(cid)
            if not info:
                skipped += 1
                continue
            driver_id, driver_name, plate = info
            if driver_id in existing_drivers or driver_id in seen_drivers:
                skipped += 1
                continue
            seen_drivers.add(driver_id)
            db.add(
                CapacityGroupMember(
                    group_id=group_id,
                    driver_id=driver_id,
                    driver_name=driver_name,
                    capacity_id=cid,
                    plate_number=plate,
                    created_by=operator_user_id,
                )
            )
            added += 1

        if added == 0 and skipped > 0:
            raise BizException("所选运力已全部在该分组中，无需重复添加")

        await db.flush()
        return {"added": added, "skipped": skipped}

    @staticmethod
    async def remove_members(
        db: AsyncSession,
        group_id: int,
        member_ids: Optional[list[int]] = None,
        driver_ids: Optional[list[int]] = None,
    ) -> dict:
        await CapacityGroupService._get_group(db, group_id)
        if not member_ids and not driver_ids:
            raise BizException("请选择要移出的成员")

        q = select(CapacityGroupMember).where(
            CapacityGroupMember.group_id == group_id,
            CapacityGroupMember.is_deleted == 0,
        )
        conds = []
        if member_ids:
            conds.append(CapacityGroupMember.id.in_(member_ids))
        if driver_ids:
            conds.append(CapacityGroupMember.driver_id.in_(driver_ids))
        q = q.where(or_(*conds))

        result = await db.execute(q)
        removed = 0
        for m in result.scalars().all():
            m.is_deleted = 1
            removed += 1
        await db.flush()
        return {"removed": removed}

    # ---------------- 计费接入 ----------------

    @staticmethod
    async def get_group_ids_for_driver(
        db: AsyncSession, driver_id: Optional[int]
    ) -> set[int]:
        """返回某司机（运力锚点）所属的启用状态分组ID集合，供计费条件预加载。"""
        if not driver_id:
            return set()
        result = await db.execute(
            select(CapacityGroupMember.group_id)
            .join(
                CapacityGroup,
                and_(
                    CapacityGroup.id == CapacityGroupMember.group_id,
                    CapacityGroup.is_deleted == 0,
                    CapacityGroup.status == 1,
                ),
            )
            .where(
                CapacityGroupMember.driver_id == driver_id,
                CapacityGroupMember.is_deleted == 0,
            )
        )
        return {int(gid) for (gid,) in result.all()}
