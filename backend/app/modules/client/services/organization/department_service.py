"""
组织架构/部门管理服务（租户库）
"""

from typing import Optional, List, Dict, Set

from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.schemas.organization.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
)

# 与前端表格列 prop 对齐；未指定排序时保持按排序号、id（与历史一致）
_DEPT_SORT_COLUMNS = {
    "createTime": BizDepartment.created_at,
}


def _dept_list_order_clauses(sort: Optional[str], order: Optional[str]):
    col = _DEPT_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [BizDepartment.sort_order, BizDepartment.id]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    if col is BizDepartment.created_at:
        return [primary, BizDepartment.sort_order, BizDepartment.id]
    return [primary]


class DepartmentService:

    @staticmethod
    async def _resolve_user_name(db: AsyncSession, user_id: Optional[int]) -> Optional[str]:
        """把负责人 user_id 解析成展示用姓名（冗余写回 leader 文本）。"""
        if not user_id:
            return None
        user = (
            await db.execute(
                select(BizUser).where(
                    BizUser.id == user_id, BizUser.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not user:
            return None
        return user.real_name or user.nickname or user.phone

    @staticmethod
    async def _subtree_user_counts(db: AsyncSession) -> Dict[int, int]:
        dept_result = await db.execute(
            select(BizDepartment).where(BizDepartment.is_deleted == 0)
        )
        dept_rows = list(dept_result.scalars().all())
        if not dept_rows:
            return {}

        dept_ids = {d.id for d in dept_rows}
        children: Dict[int, List[int]] = {}
        for d in dept_rows:
            pid = d.parent_id
            if pid and pid in dept_ids:
                children.setdefault(pid, []).append(d.id)

        roots = [
            d.id for d in dept_rows
            if d.parent_id == 0 or d.parent_id not in dept_ids
        ]

        user_result = await db.execute(
            select(BizUser.id, BizUser.department_id).where(
                BizUser.is_deleted == 0,
                BizUser.department_id.isnot(None),
            )
        )
        direct: Dict[int, Set[int]] = {did: set() for did in dept_ids}
        for uid, dep_id in user_result.all():
            if dep_id in dept_ids:
                direct[dep_id].add(uid)

        memo: Dict[int, Set[int]] = {}

        def collect(did: int) -> Set[int]:
            if did in memo:
                return memo[did]
            merged: Set[int] = set(direct.get(did, ()))
            for c in children.get(did, []):
                merged |= collect(c)
            memo[did] = merged
            return merged

        for r in roots:
            collect(r)
        for did in dept_ids:
            if did not in memo:
                collect(did)

        return {did: len(s) for did, s in memo.items()}

    @staticmethod
    async def page_departments(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        organization_name: Optional[str] = None,
        organization_type: Optional[str] = None,
    ) -> dict:
        """分页查询部门"""
        base = select(BizDepartment).where(BizDepartment.is_deleted == 0)

        if organization_name:
            base = base.where(BizDepartment.dept_name.contains(organization_name))
        if organization_type:
            base = base.where(BizDepartment.dept_type == organization_type)

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(BizDepartment.sort_order, BizDepartment.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = [DepartmentOut.from_model(d) for d in result.scalars().all()]

        return {
            "list": [item.model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def list_departments(
        db: AsyncSession,
        organization_name: Optional[str] = None,
        organization_type: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[DepartmentOut]:
        """获取全部部门列表（平铺，前端组装树形）"""
        base = select(BizDepartment).where(BizDepartment.is_deleted == 0)

        if organization_name:
            base = base.where(BizDepartment.dept_name.contains(organization_name))
        if organization_type:
            base = base.where(BizDepartment.dept_type == organization_type)

        result = await db.execute(
            base.order_by(*_dept_list_order_clauses(sort, order))
        )
        counts = await DepartmentService._subtree_user_counts(db)
        items: List[DepartmentOut] = []
        for d in result.scalars().all():
            out = DepartmentOut.from_model(d)
            items.append(
                out.model_copy(update={"userCount": counts.get(d.id, 0)})
            )
        return items

    @staticmethod
    async def get_department_tree(
        db: AsyncSession,
        organization_name: Optional[str] = None,
    ) -> List[dict]:
        """获取部门树形结构"""
        base = select(BizDepartment).where(BizDepartment.is_deleted == 0)
        if organization_name:
            base = base.where(BizDepartment.dept_name.contains(organization_name))

        result = await db.execute(
            base.order_by(BizDepartment.sort_order, BizDepartment.id)
        )
        all_depts = result.scalars().all()

        dept_map = {}
        for d in all_depts:
            dept_map[d.id] = DepartmentOut.from_model(d).model_dump()
            dept_map[d.id]["children"] = []

        tree = []
        for d in all_depts:
            node = dept_map[d.id]
            if d.parent_id == 0 or d.parent_id not in dept_map:
                tree.append(node)
            else:
                dept_map[d.parent_id]["children"].append(node)

        counts = await DepartmentService._subtree_user_counts(db)
        for did, node in dept_map.items():
            node["userCount"] = counts.get(did, 0)

        return tree

    @staticmethod
    async def create_department(
        db: AsyncSession, data: DepartmentCreate
    ) -> BizDepartment:
        leader_text = data.leader
        if data.leaderUserId and not leader_text:
            leader_text = await DepartmentService._resolve_user_name(
                db, data.leaderUserId
            )
        dept = BizDepartment(
            parent_id=data.parentId,
            dept_name=data.organizationName,
            dept_code=data.organizationCode,
            dept_type=data.organizationType,
            leader=leader_text,
            leader_user_id=data.leaderUserId,
            phone=data.phone,
            sort_order=data.sortNumber,
            remark=data.comments,
        )
        db.add(dept)
        await db.flush()
        await db.refresh(dept)
        return dept

    @staticmethod
    async def update_department(
        db: AsyncSession, dept_id: int, data: DepartmentUpdate
    ) -> BizDepartment:
        result = await db.execute(
            select(BizDepartment).where(
                BizDepartment.id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        dept = result.scalar_one_or_none()
        if not dept:
            raise BizException("部门不存在")

        field_map = {
            "parentId": "parent_id",
            "organizationName": "dept_name",
            "organizationCode": "dept_code",
            "organizationType": "dept_type",
            "leader": "leader",
            "leaderUserId": "leader_user_id",
            "phone": "phone",
            "sortNumber": "sort_order",
            "status": "status",
            "comments": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(dept, model_field, val)

        # 负责人变更时，按 user_id 刷新冗余的 leader 姓名文本
        if data.leaderUserId is not None:
            dept.leader = await DepartmentService._resolve_user_name(
                db, data.leaderUserId
            )

        await db.flush()
        await db.refresh(dept)
        return dept

    @staticmethod
    async def delete_department(db: AsyncSession, dept_id: int) -> None:
        result = await db.execute(
            select(BizDepartment).where(
                BizDepartment.id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        dept = result.scalar_one_or_none()
        if not dept:
            raise BizException("部门不存在")

        children = await db.execute(
            select(BizDepartment).where(
                BizDepartment.parent_id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        if children.scalars().first():
            raise BizException("该部门下有子部门，无法删除")

        users = await db.execute(
            select(BizUser).where(
                BizUser.department_id == dept_id,
                BizUser.is_deleted == 0,
            )
        )
        if users.scalars().first():
            raise BizException("该部门下存在员工，无法删除")

        dept.is_deleted = 1
        await db.flush()
