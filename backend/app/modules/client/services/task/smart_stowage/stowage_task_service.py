"""
智能配载生成任务服务（认领 / 状态回写）

沿用承运运费计算任务表（CarrierFreightCalcTaskService）的认领模式，供：
  - 同步路径：API 内 create -> claim_one -> 直接执行；
  - 异步路径（预留）：worker 扫 pending 认领执行。
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.smart_stowage import SmartStowagePlanTask
from app.modules.client.services.task.smart_stowage.constants import (
    TASK_FAILED,
    TASK_PENDING,
    TASK_RUNNING,
    TASK_SUCCESS,
)


class SmartStowageTaskService:

    # ---------- 写入 ----------

    @staticmethod
    async def create_task(
        db: AsyncSession,
        *,
        filter_payload: Optional[dict[str, Any]] = None,
        params_payload: Optional[dict[str, Any]] = None,
        triggered_by_user_id: Optional[int] = None,
        triggered_by_name: Optional[str] = None,
    ) -> SmartStowagePlanTask:
        task = SmartStowagePlanTask(
            status=TASK_PENDING,
            filter_json=json.dumps(filter_payload or {}, ensure_ascii=False),
            params_json=json.dumps(params_payload or {}, ensure_ascii=False),
            triggered_by_user_id=triggered_by_user_id,
            triggered_by_name=triggered_by_name,
        )
        db.add(task)
        await db.flush()
        return task

    # ---------- 认领 / 状态回写 ----------

    @staticmethod
    async def claim_one(db: AsyncSession, task_id: int) -> bool:
        """将指定任务从 pending 置为 running（幂等抢占）。成功返回 True。"""
        r = await db.execute(
            update(SmartStowagePlanTask)
            .where(
                SmartStowagePlanTask.id == task_id,
                SmartStowagePlanTask.status == TASK_PENDING,
            )
            .values(status=TASK_RUNNING, started_at=datetime.now())
        )
        return (r.rowcount or 0) > 0

    @staticmethod
    async def claim_pending(
        db: AsyncSession, batch_size: int = 10
    ) -> list[SmartStowagePlanTask]:
        ids_q = await db.execute(
            select(SmartStowagePlanTask.id)
            .where(
                SmartStowagePlanTask.status == TASK_PENDING,
                SmartStowagePlanTask.is_deleted == 0,
            )
            .order_by(SmartStowagePlanTask.created_at.asc())
            .limit(batch_size)
        )
        ids = [row[0] for row in ids_q.all()]
        if not ids:
            return []
        await db.execute(
            update(SmartStowagePlanTask)
            .where(
                SmartStowagePlanTask.id.in_(ids),
                SmartStowagePlanTask.status == TASK_PENDING,
            )
            .values(status=TASK_RUNNING, started_at=datetime.now())
        )
        r = await db.execute(
            select(SmartStowagePlanTask).where(
                SmartStowagePlanTask.id.in_(ids),
                SmartStowagePlanTask.status == TASK_RUNNING,
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def mark_success(
        db: AsyncSession,
        task_id: int,
        *,
        candidate_count: int,
        plan_count: int,
    ) -> None:
        await db.execute(
            update(SmartStowagePlanTask)
            .where(SmartStowagePlanTask.id == task_id)
            .values(
                status=TASK_SUCCESS,
                candidate_count=candidate_count,
                plan_count=plan_count,
                error_message=None,
                finished_at=datetime.now(),
            )
        )

    @staticmethod
    async def mark_failed(
        db: AsyncSession, task_id: int, error_message: str
    ) -> None:
        r = await db.execute(
            select(SmartStowagePlanTask).where(
                SmartStowagePlanTask.id == task_id
            )
        )
        task = r.scalar_one_or_none()
        if not task:
            return
        new_retry = (task.retry_count or 0) + 1
        if new_retry < (task.max_retry_count or 3):
            task.retry_count = new_retry
            task.status = TASK_PENDING
            task.finished_at = None
        else:
            task.retry_count = new_retry
            task.status = TASK_FAILED
            task.finished_at = datetime.now()
        task.error_message = error_message[:1000]
        await db.flush()

    @staticmethod
    async def get(db: AsyncSession, task_id: int) -> Optional[SmartStowagePlanTask]:
        r = await db.execute(
            select(SmartStowagePlanTask).where(
                SmartStowagePlanTask.id == task_id,
                SmartStowagePlanTask.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def incr_adopted(db: AsyncSession, task_id: int) -> None:
        task = await SmartStowageTaskService.get(db, task_id)
        if task is not None:
            task.adopted_count = (task.adopted_count or 0) + 1
            await db.flush()
