"""
成本计算任务服务（异步重算，与收入侧 FreightCalcTaskService 对称）
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.cost_calc_task import CostCalcTask


# ---- 任务类型枚举 ----
TASK_TASK_DISPATCHED = "task_dispatched"
TASK_TASK_CHANGED = "task_changed"
TASK_POLICY_CHANGED = "policy_changed"
TASK_RULE_CHANGED = "rule_changed"
TASK_MANUAL_RECALC = "manual_recalc"


class CostCalcTaskService:

    # ---------- 写入 ----------

    @staticmethod
    async def enqueue_task_recalc(
        db: AsyncSession,
        task_id: int,
        *,
        task_type: str = TASK_TASK_CHANGED,
        priority: int = 0,
        triggered_by_user_id: Optional[int] = None,
    ) -> CostCalcTask:
        existing = await db.execute(
            select(CostCalcTask).where(
                CostCalcTask.task_type == task_type,
                CostCalcTask.target_type == "task",
                CostCalcTask.target_id == task_id,
                CostCalcTask.status.in_(("pending", "running")),
                CostCalcTask.is_deleted == 0,
            ).order_by(CostCalcTask.id.desc()).limit(1)
        )
        old = existing.scalar_one_or_none()
        if old:
            if priority > (old.priority or 0):
                old.priority = priority
            await db.flush()
            return old

        task = CostCalcTask(
            task_type=task_type,
            target_type="task",
            target_id=task_id,
            task_id=task_id,
            status="pending",
            priority=priority,
            triggered_by_user_id=triggered_by_user_id,
        )
        db.add(task)
        await db.flush()
        return task

    @staticmethod
    async def enqueue_many_tasks(
        db: AsyncSession,
        task_ids: list[int],
        *,
        task_type: str,
        source_target_type: str = "rule",
        source_target_id: Optional[int] = None,
        priority: int = 0,
        triggered_by_user_id: Optional[int] = None,
    ) -> int:
        if not task_ids:
            return 0
        r = await db.execute(
            select(CostCalcTask.target_id).where(
                CostCalcTask.task_type == task_type,
                CostCalcTask.target_type == "task",
                CostCalcTask.target_id.in_(task_ids),
                CostCalcTask.status.in_(("pending", "running")),
                CostCalcTask.is_deleted == 0,
            )
        )
        existing_ids = {row[0] for row in r.all()}
        added = 0
        for tid in task_ids:
            if tid in existing_ids:
                continue
            db.add(CostCalcTask(
                task_type=task_type,
                target_type="task",
                target_id=tid,
                task_id=tid,
                status="pending",
                priority=priority,
                triggered_by_user_id=triggered_by_user_id,
                error_message=(
                    f"由 {source_target_type}#{source_target_id} 变更触发"
                    if source_target_id else None
                ),
            ))
            added += 1
        await db.flush()
        return added

    # ---------- worker 认领 / 状态回写 ----------

    @staticmethod
    async def claim_pending(
        db: AsyncSession, batch_size: int = 50
    ) -> list[CostCalcTask]:
        ids_q = await db.execute(
            select(CostCalcTask.id).where(
                CostCalcTask.status == "pending",
                CostCalcTask.is_deleted == 0,
            ).order_by(
                CostCalcTask.priority.desc(),
                CostCalcTask.created_at.asc(),
            ).limit(batch_size)
        )
        ids = [row[0] for row in ids_q.all()]
        if not ids:
            return []
        await db.execute(
            update(CostCalcTask)
            .where(CostCalcTask.id.in_(ids), CostCalcTask.status == "pending")
            .values(status="running", started_at=datetime.now())
        )
        r = await db.execute(
            select(CostCalcTask).where(
                CostCalcTask.id.in_(ids), CostCalcTask.status == "running",
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def mark_success(db: AsyncSession, task_id: int) -> None:
        await db.execute(
            update(CostCalcTask)
            .where(CostCalcTask.id == task_id)
            .values(status="success", finished_at=datetime.now(), error_message=None)
        )

    @staticmethod
    async def mark_failed(
        db: AsyncSession, task_id: int, error_message: str
    ) -> None:
        r = await db.execute(
            select(CostCalcTask).where(CostCalcTask.id == task_id)
        )
        task = r.scalar_one_or_none()
        if not task:
            return
        new_retry = (task.retry_count or 0) + 1
        if new_retry < (task.max_retry_count or 3):
            task.retry_count = new_retry
            task.status = "pending"
            task.error_message = error_message[:1000]
            task.finished_at = None
        else:
            task.retry_count = new_retry
            task.status = "failed"
            task.finished_at = datetime.now()
            task.error_message = error_message[:1000]
        await db.flush()

    # ---------- 查询 ----------

    @staticmethod
    async def page_tasks(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        task_id: Optional[int] = None,
    ) -> dict:
        base = select(CostCalcTask).where(CostCalcTask.is_deleted == 0)
        if status:
            base = base.where(CostCalcTask.status == status)
        if task_type:
            base = base.where(CostCalcTask.task_type == task_type)
        if task_id:
            base = base.where(CostCalcTask.task_id == task_id)

        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        r = await db.execute(
            base.order_by(CostCalcTask.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = []
        for t in r.scalars().all():
            items.append({
                "id": t.id,
                "taskType": t.task_type,
                "targetType": t.target_type,
                "targetId": t.target_id,
                "taskId": t.task_id,
                "status": t.status,
                "priority": t.priority,
                "retryCount": t.retry_count,
                "maxRetryCount": t.max_retry_count,
                "errorMessage": t.error_message,
                "startedAt": t.started_at,
                "finishedAt": t.finished_at,
                "createdAt": t.created_at,
            })
        return {"list": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def retry_task(db: AsyncSession, task_id: int) -> None:
        await db.execute(
            update(CostCalcTask)
            .where(CostCalcTask.id == task_id)
            .values(
                status="pending", retry_count=0, error_message=None,
                started_at=None, finished_at=None,
            )
        )
