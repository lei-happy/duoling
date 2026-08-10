"""
任务单状态事件 Service

所有改写 ``task.status`` 的地方都应经由 :meth:`TaskStatusEventService.apply_status`，
它同时完成三件事：写状态、刷新 ``stage_entered_at``、落一条 append-only 事件。

放在独立模块而不是 ``task_service`` 里，是因为 ``task_waybill_item_service`` 的聚合
跳转（1↔2 / 3↔4 / 4↔5）也要落事件，而它被 ``task_service`` 反向导入，直接互引会成环。
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_status_event import (
    TASK_EVENT_SOURCE_CLIENT,
    TaskStatusEvent,
)


class TaskStatusEventService:
    """状态事件写入与读取"""

    @staticmethod
    def record(
        db: AsyncSession,
        task: Task,
        *,
        event_type: int,
        from_status: Optional[int],
        to_status: Optional[int],
        source: int = TASK_EVENT_SOURCE_CLIENT,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        reason: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
        event_time: Optional[datetime] = None,
    ) -> Optional[TaskStatusEvent]:
        """落一条事件。``task.id`` 尚未生成时静默跳过（调用方需先 flush）。"""
        if task.id is None:
            return None
        event = TaskStatusEvent(
            task_id=int(task.id),
            task_no=task.task_no,
            event_type=int(event_type),
            from_status=None if from_status is None else int(from_status),
            to_status=None if to_status is None else int(to_status),
            source=int(source),
            operator_id=operator_id,
            operator_name=(operator_name or None),
            reason=(reason.strip()[:255] if reason and reason.strip() else None),
            payload_snapshot=payload,
            event_time=event_time or datetime.now(),
        )
        db.add(event)
        return event

    @staticmethod
    def apply_status(
        db: AsyncSession,
        task: Task,
        new_status: int,
        *,
        event_type: int,
        source: int = TASK_EVENT_SOURCE_CLIENT,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        reason: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
        event_time: Optional[datetime] = None,
    ) -> Optional[TaskStatusEvent]:
        """写状态 + 刷新阶段进入时间 + 落事件。

        状态未变化时（如重复提交同一动作）既不落事件，也**不**刷新
        ``stage_entered_at`` —— 否则「本阶段停留」会被无声清零。
        """
        old = int(task.status) if task.status is not None else None
        new = int(new_status)
        happened_at = event_time or datetime.now()
        task.status = new
        if old == new:
            if task.stage_entered_at is None:
                task.stage_entered_at = happened_at
            return None
        task.stage_entered_at = happened_at
        return TaskStatusEventService.record(
            db, task,
            event_type=event_type,
            from_status=old,
            to_status=new,
            source=source,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=reason,
            payload=payload,
            event_time=happened_at,
        )

    @staticmethod
    async def list_events(
        db: AsyncSession, task_id: int
    ) -> list[TaskStatusEvent]:
        """按时间正序返回某任务的全部状态事件。"""
        r = await db.execute(
            select(TaskStatusEvent)
            .where(
                TaskStatusEvent.task_id == task_id,
                TaskStatusEvent.is_deleted == 0,
            )
            .order_by(TaskStatusEvent.event_time.asc(), TaskStatusEvent.id.asc())
        )
        return list(r.scalars().all())
