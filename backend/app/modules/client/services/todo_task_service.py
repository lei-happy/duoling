"""
工作台待办（平台库 sys_todo_task + 租户库 biz_user 校验）
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.schemas.workbench.todo_task import (
    AssignableUserOut,
    ConsoleTodoTaskOut,
    TodoTaskCreate,
    TodoTaskOut,
    TodoTaskUpdate,
)
from app.modules.console.models.system.user import User
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.todo.sys_todo_task import SysTodoTask


def _biz_display_name(u: BizUser) -> str:
    return (u.real_name or u.nickname or u.phone or "").strip() or str(u.id)


def _task_to_out(row: SysTodoTask) -> dict:
    return TodoTaskOut(
        id=row.id,
        tenant_code=row.tenant_code,
        title=row.title,
        description=row.description,
        creator_id=row.creator_id,
        assignee_id=row.assignee_id,
        creator_name=row.creator_name,
        assignee_name=row.assignee_name,
        due_time=row.due_time,
        priority=row.priority,
        status=row.status,
        completed_time=row.completed_time,
        create_time=row.created_at,
        update_time=row.updated_at,
    ).model_dump()


class TodoTaskService:
    @staticmethod
    async def _get_platform_user_phone(pdb: AsyncSession, sys_user_id: int) -> str:
        r = await pdb.execute(
            select(User.phone).where(User.id == sys_user_id, User.is_deleted == 0)
        )
        phone = r.scalar_one_or_none()
        if not phone:
            raise BizException("用户不存在")
        return phone

    @staticmethod
    async def resolve_biz_user_id(
        pdb: AsyncSession,
        tdb: AsyncSession,
        sys_user_id: int,
    ) -> BizUser:
        phone = await TodoTaskService._get_platform_user_phone(pdb, sys_user_id)
        r = await tdb.execute(
            select(BizUser).where(
                BizUser.phone == phone,
                BizUser.is_deleted == 0,
            )
        )
        bu = r.scalar_one_or_none()
        if not bu:
            raise BizException("当前账号在当前企业下无员工档案，无法使用待办")
        if bu.status != 0:
            raise BizException("员工已停用，无法使用待办")
        return bu

    @staticmethod
    async def _get_assignable_biz_user(
        tdb: AsyncSession,
        biz_user_id: int,
    ) -> BizUser:
        r = await tdb.execute(
            select(BizUser).where(
                BizUser.id == biz_user_id,
                BizUser.is_deleted == 0,
            )
        )
        u = r.scalar_one_or_none()
        if not u:
            raise BizException("指派的员工不存在")
        if u.status != 0:
            raise BizException("指派的员工已停用")
        return u

    @staticmethod
    async def list_assignable_users(
        tdb: AsyncSession,
        keyword: Optional[str] = None,
        limit: int = 50,
    ) -> List[dict]:
        q = select(BizUser).where(BizUser.is_deleted == 0, BizUser.status == 0)
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            q = q.where(
                (BizUser.real_name.like(kw))
                | (BizUser.nickname.like(kw))
                | (BizUser.phone.like(kw))
            )
        q = q.order_by(BizUser.id.desc()).limit(min(limit, 200))
        r = await tdb.execute(q)
        users = r.scalars().all()
        return [
            AssignableUserOut(id=u.id, display_name=_biz_display_name(u)).model_dump()
            for u in users
        ]

    @staticmethod
    async def create_task(
        pdb: AsyncSession,
        tdb: AsyncSession,
        tenant_code: str,
        sys_user_id: int,
        body: TodoTaskCreate,
    ) -> dict:
        creator = await TodoTaskService.resolve_biz_user_id(pdb, tdb, sys_user_id)
        assignee_name = None
        assignee_id = body.assignee_id
        if assignee_id is not None:
            assignee = await TodoTaskService._get_assignable_biz_user(tdb, assignee_id)
            assignee_name = _biz_display_name(assignee)

        completed_time = None
        if body.status == 2:
            completed_time = datetime.now()

        row = SysTodoTask(
            tenant_code=tenant_code,
            title=body.title.strip(),
            description=body.description,
            creator_id=creator.id,
            assignee_id=assignee_id,
            creator_name=_biz_display_name(creator),
            assignee_name=assignee_name,
            due_time=body.due_time,
            priority=body.priority,
            status=body.status,
            completed_time=completed_time,
        )
        pdb.add(row)
        await pdb.flush()
        await pdb.refresh(row)
        return _task_to_out(row)

    @staticmethod
    async def get_task_for_tenant(
        pdb: AsyncSession,
        task_id: int,
        tenant_code: str,
    ) -> Optional[SysTodoTask]:
        r = await pdb.execute(
            select(SysTodoTask).where(
                SysTodoTask.id == task_id,
                SysTodoTask.tenant_code == tenant_code,
                SysTodoTask.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def page_tasks(
        pdb: AsyncSession,
        tdb: AsyncSession,
        tenant_code: str,
        sys_user_id: int,
        *,
        page: int,
        page_size: int,
        status: Optional[int],
        my_tasks: bool,
    ) -> dict:
        q = select(SysTodoTask).where(
            SysTodoTask.tenant_code == tenant_code,
            SysTodoTask.is_deleted == 0,
        )
        if status is not None:
            q = q.where(SysTodoTask.status == status)
        if my_tasks:
            me = await TodoTaskService.resolve_biz_user_id(pdb, tdb, sys_user_id)
            # 我创建的、或指派给我的（无指派人时仅创建人可见）
            q = q.where(
                or_(
                    SysTodoTask.assignee_id == me.id,
                    SysTodoTask.creator_id == me.id,
                )
            )

        count_q = select(func.count()).select_from(q.subquery())
        total = (await pdb.execute(count_q)).scalar() or 0

        pages = max(1, math.ceil(total / page_size)) if page_size else 1
        q = q.order_by(SysTodoTask.id.desc())
        q = q.offset((page - 1) * page_size).limit(page_size)
        r = await pdb.execute(q)
        rows = r.scalars().all()
        return {
            "items": [_task_to_out(x) for x in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    @staticmethod
    async def stats(
        pdb: AsyncSession,
        tdb: AsyncSession,
        tenant_code: str,
        sys_user_id: int,
        my_tasks: bool,
    ) -> dict:
        cond = [
            SysTodoTask.tenant_code == tenant_code,
            SysTodoTask.is_deleted == 0,
        ]
        if my_tasks:
            me = await TodoTaskService.resolve_biz_user_id(pdb, tdb, sys_user_id)
            cond.append(
                or_(
                    SysTodoTask.assignee_id == me.id,
                    SysTodoTask.creator_id == me.id,
                )
            )

        async def _count(extra=None):
            c = list(cond)
            if extra is not None:
                c.append(extra)
            q = select(func.count()).select_from(SysTodoTask).where(*c)
            return (await pdb.execute(q)).scalar() or 0

        total = await _count()
        pending = await _count(SysTodoTask.status == 0)
        in_progress = await _count(SysTodoTask.status == 1)
        completed = await _count(SysTodoTask.status == 2)
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
        }

    @staticmethod
    async def apply_task_update(
        pdb: AsyncSession,
        tdb: AsyncSession,
        tenant_code: str,
        task_id: int,
        body: TodoTaskUpdate,
        patch_keys: set,
    ) -> dict:
        row = await TodoTaskService.get_task_for_tenant(pdb, task_id, tenant_code)
        if not row:
            raise BizException("待办不存在")

        if "title" in patch_keys and body.title is not None:
            row.title = body.title.strip()
        if "description" in patch_keys:
            row.description = body.description  # 含显式置空
        if "priority" in patch_keys and body.priority is not None:
            row.priority = body.priority
        if "due_time" in patch_keys:
            row.due_time = body.due_time
        if "status" in patch_keys and body.status is not None:
            row.status = body.status
            if body.status == 2:
                row.completed_time = datetime.now()
            else:
                row.completed_time = None

        if "assignee_id" in patch_keys:
            if body.assignee_id is None:
                row.assignee_id = None
                row.assignee_name = None
            else:
                assignee = await TodoTaskService._get_assignable_biz_user(tdb, body.assignee_id)
                row.assignee_id = assignee.id
                row.assignee_name = _biz_display_name(assignee)

        await pdb.flush()
        await pdb.refresh(row)
        return _task_to_out(row)

    @staticmethod
    async def set_status(
        pdb: AsyncSession,
        tenant_code: str,
        task_id: int,
        status: int,
    ) -> dict:
        row = await TodoTaskService.get_task_for_tenant(pdb, task_id, tenant_code)
        if not row:
            raise BizException("待办不存在")
        row.status = status
        if status == 2:
            row.completed_time = datetime.now()
        else:
            row.completed_time = None
        await pdb.flush()
        await pdb.refresh(row)
        return _task_to_out(row)

    @staticmethod
    async def delete_task(
        pdb: AsyncSession,
        tenant_code: str,
        task_id: int,
    ) -> None:
        row = await TodoTaskService.get_task_for_tenant(pdb, task_id, tenant_code)
        if not row:
            raise BizException("待办不存在")
        row.is_deleted = 1
        await pdb.flush()

    # ---- Console ----

    @staticmethod
    async def page_for_console(
        pdb: AsyncSession,
        *,
        page: int,
        page_size: int,
        tenant_code: Optional[str],
        status: Optional[int],
    ) -> Tuple[List[dict], int]:
        filters = [SysTodoTask.is_deleted == 0]
        if tenant_code:
            filters.append(SysTodoTask.tenant_code == tenant_code)
        if status is not None:
            filters.append(SysTodoTask.status == status)

        count_q = select(func.count()).select_from(SysTodoTask).where(*filters)
        total = (await pdb.execute(count_q)).scalar() or 0

        q = (
            select(SysTodoTask, Tenant.tenant_name)
            .outerjoin(Tenant, Tenant.tenant_code == SysTodoTask.tenant_code)
            .where(*filters)
            .order_by(SysTodoTask.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        r = await pdb.execute(q)
        items = []
        for row, tenant_name in r.all():
            d = _task_to_out(row)
            co = ConsoleTodoTaskOut(**d, tenant_name=tenant_name)
            items.append(co.model_dump())
        return items, total
