"""审批中心 - 审批人解析

把节点「审批人类型 + 配置」动态翻译成具体 user_id 列表。只读组织数据，不写。
类型 4/5 依赖部门 leader_user_id 与用户 supervisor_user_id（组织/用户模块维护）。

详见《08.审批中心/01.审批引擎核心设计》§四。
"""

from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.user.biz_user_role import BizUserRole
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.services.approval import constants as C


class ApproverResolver:
    @staticmethod
    async def resolve(
        db: AsyncSession,
        *,
        approver_type: int,
        approver_config: dict | None,
        initiator_id: int,
        initiator_dept_id: int | None,
        variables: dict | None,
    ) -> List[int]:
        cfg = approver_config or {}
        vars_ = variables or {}

        if approver_type == C.APPROVER_USER:
            ids = cfg.get("user_ids") or []
        elif approver_type == C.APPROVER_ROLE:
            ids = await ApproverResolver._users_by_roles(db, cfg.get("role_ids") or [])
        elif approver_type == C.APPROVER_DEPT:
            ids = await ApproverResolver._users_by_depts(
                db, cfg.get("dept_ids") or [], bool(cfg.get("include_child", True))
            )
        elif approver_type == C.APPROVER_DEPT_LEADER:
            dept_id = (
                initiator_dept_id
                if cfg.get("dept_ref") == "initiator"
                else cfg.get("dept_id")
            )
            ids = await ApproverResolver._dept_leader(db, dept_id)
        elif approver_type == C.APPROVER_SUPERVISOR:
            ids = await ApproverResolver._supervisor_chain(
                db, initiator_id, int(cfg.get("level", 1))
            )
        elif approver_type == C.APPROVER_INITIATOR_PICK:
            ids = vars_.get("picked_approvers") or []
        elif approver_type == C.APPROVER_INITIATOR:
            ids = [initiator_id]
        else:
            ids = []

        # 去重 + 过滤无效；可选排除发起人
        result: List[int] = []
        skip_initiator = bool(cfg.get("skip_initiator", False))
        for uid in ids:
            try:
                uid = int(uid)
            except (TypeError, ValueError):
                continue
            if uid <= 0 or uid in result:
                continue
            if skip_initiator and uid == initiator_id:
                continue
            result.append(uid)
        return result

    @staticmethod
    async def _users_by_roles(db: AsyncSession, role_ids: list) -> List[int]:
        if not role_ids:
            return []
        rows = await db.execute(
            select(BizUserRole.user_id)
            .where(
                BizUserRole.role_id.in_(role_ids),
                BizUserRole.is_deleted == 0,
            )
        )
        return [r[0] for r in rows.all()]

    @staticmethod
    async def _users_by_depts(
        db: AsyncSession, dept_ids: list, include_child: bool
    ) -> List[int]:
        if not dept_ids:
            return []
        target_ids = set(int(d) for d in dept_ids)
        if include_child:
            target_ids |= await ApproverResolver._collect_child_dept_ids(db, target_ids)
        rows = await db.execute(
            select(BizUser.id).where(
                BizUser.department_id.in_(target_ids),
                BizUser.is_deleted == 0,
            )
        )
        return [r[0] for r in rows.all()]

    @staticmethod
    async def _collect_child_dept_ids(db: AsyncSession, root_ids: set) -> set:
        """加载全部部门，BFS 收集子孙部门 id。"""
        rows = await db.execute(
            select(BizDepartment.id, BizDepartment.parent_id).where(
                BizDepartment.is_deleted == 0
            )
        )
        children: dict[int, list[int]] = {}
        for did, pid in rows.all():
            children.setdefault(pid or 0, []).append(did)
        collected: set = set()
        stack = list(root_ids)
        while stack:
            cur = stack.pop()
            for child in children.get(cur, []):
                if child not in collected:
                    collected.add(child)
                    stack.append(child)
        return collected

    @staticmethod
    async def _dept_leader(db: AsyncSession, dept_id) -> List[int]:
        if not dept_id:
            return []
        dept = (
            await db.execute(
                select(BizDepartment).where(
                    BizDepartment.id == dept_id, BizDepartment.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not dept or not dept.leader_user_id:
            return []
        return [dept.leader_user_id]

    @staticmethod
    async def _supervisor_chain(
        db: AsyncSession, user_id: int, level: int
    ) -> List[int]:
        cur = user_id
        visited = {cur}
        for _ in range(max(1, min(level, 10))):
            user = (
                await db.execute(
                    select(BizUser).where(
                        BizUser.id == cur, BizUser.is_deleted == 0
                    )
                )
            ).scalar_one_or_none()
            sup = user.supervisor_user_id if user else None
            if not sup or sup in visited:
                return []
            visited.add(sup)
            cur = sup
        return [cur]
