"""能源同步任务队列"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.sync_task import EnergySyncTask
from app.modules.client.services.energy.constants import (
    SYNC_FAILED,
    SYNC_PENDING,
    SYNC_RUNNING,
    SYNC_SUCCESS,
)


class EnergySyncTaskService:

    @staticmethod
    async def enqueue(
        db: AsyncSession,
        *,
        task_type: str,
        connector_id: Optional[int] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        payload_json: Optional[str] = None,
        priority: int = 0,
    ) -> EnergySyncTask:
        existed = (await db.execute(
            select(EnergySyncTask).where(
                EnergySyncTask.task_type == task_type,
                EnergySyncTask.connector_id == connector_id,
                EnergySyncTask.target_type == target_type,
                EnergySyncTask.target_id == target_id,
                EnergySyncTask.status.in_((SYNC_PENDING, SYNC_RUNNING)),
                EnergySyncTask.is_deleted == 0,
            )
        )).scalar_one_or_none()
        if existed:
            if priority > (existed.priority or 0):
                existed.priority = priority
            return existed
        obj = EnergySyncTask(
            task_type=task_type,
            connector_id=connector_id,
            target_type=target_type,
            target_id=target_id,
            payload_json=payload_json,
            priority=priority,
            status=SYNC_PENDING,
        )
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def claim_pending(db: AsyncSession, batch_size: int = 10) -> list[EnergySyncTask]:
        rows = (await db.execute(
            select(EnergySyncTask)
            .where(
                EnergySyncTask.status == SYNC_PENDING,
                EnergySyncTask.is_deleted == 0,
            )
            .order_by(EnergySyncTask.priority.desc(), EnergySyncTask.id.asc())
            .limit(batch_size)
        )).scalars().all()
        ids = [r.id for r in rows]
        if not ids:
            return []
        await db.execute(
            update(EnergySyncTask)
            .where(EnergySyncTask.id.in_(ids), EnergySyncTask.status == SYNC_PENDING)
            .values(status=SYNC_RUNNING, started_at=datetime.now())
        )
        await db.flush()
        return list((await db.execute(
            select(EnergySyncTask).where(EnergySyncTask.id.in_(ids))
        )).scalars().all())

    @staticmethod
    async def mark_success(db: AsyncSession, task_id: int) -> None:
        r = await db.execute(select(EnergySyncTask).where(EnergySyncTask.id == task_id))
        t = r.scalar_one_or_none()
        if t:
            t.status = SYNC_SUCCESS
            t.finished_at = datetime.now()
            t.error_message = None

    @staticmethod
    async def mark_failed(db: AsyncSession, task_id: int, error: str) -> None:
        r = await db.execute(select(EnergySyncTask).where(EnergySyncTask.id == task_id))
        t = r.scalar_one_or_none()
        if not t:
            return
        t.retry_count = (t.retry_count or 0) + 1
        t.error_message = (error or "")[:1000]
        t.finished_at = datetime.now()
        if t.retry_count < (t.max_retry_count or 3):
            t.status = SYNC_PENDING
        else:
            t.status = SYNC_FAILED
