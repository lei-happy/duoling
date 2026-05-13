"""
运费计算任务服务（Phase 3 - 异步重算）

职责：
  - enqueue_*       : 提供给上游业务（运单/合同/运价 service）写任务
  - claim_pending   : worker 调用：原子地认领一批 pending 任务（mark running）
  - mark_success / mark_failed : worker 完成后回写状态
  - page_tasks      : 给运维/前端做查询
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.freight_calc_task import FreightCalcTask


# ---- 任务类型枚举（字符串常量） ----
TASK_WAYBILL_CHANGED = "waybill_changed"
TASK_CONTRACT_CHANGED = "contract_changed"
TASK_RULE_CHANGED = "rule_changed"
TASK_MANUAL_RECALC = "manual_recalc"
TASK_BATCH_IMPORT = "batch_import"


class FreightCalcTaskService:

    # ---------- 写入 ----------

    @staticmethod
    async def enqueue_waybill_recalc(
        db: AsyncSession,
        waybill_id: int,
        *,
        task_type: str = TASK_WAYBILL_CHANGED,
        priority: int = 0,
        triggered_by_user_id: Optional[int] = None,
    ) -> FreightCalcTask:
        """对单个运单入队重算任务。

        简单去重：若该 waybill 已存在 pending/running 的同类型任务则复用。
        """
        existing = await db.execute(
            select(FreightCalcTask).where(
                FreightCalcTask.task_type == task_type,
                FreightCalcTask.target_type == "waybill",
                FreightCalcTask.target_id == waybill_id,
                FreightCalcTask.status.in_(("pending", "running")),
                FreightCalcTask.is_deleted == 0,
            ).order_by(FreightCalcTask.id.desc()).limit(1)
        )
        old = existing.scalar_one_or_none()
        if old:
            # 提升优先级（不创建新行，减少表噪音）
            if priority > (old.priority or 0):
                old.priority = priority
            await db.flush()
            return old

        task = FreightCalcTask(
            task_type=task_type,
            target_type="waybill",
            target_id=waybill_id,
            waybill_id=waybill_id,
            status="pending",
            priority=priority,
            triggered_by_user_id=triggered_by_user_id,
        )
        db.add(task)
        await db.flush()
        return task

    @staticmethod
    async def enqueue_many_waybills(
        db: AsyncSession,
        waybill_ids: list[int],
        *,
        task_type: str,
        source_target_type: str = "rule",
        source_target_id: Optional[int] = None,
        priority: int = 0,
        triggered_by_user_id: Optional[int] = None,
    ) -> int:
        """批量入队（合同/规则变更触发）。

        每个运单单独建任务，便于 worker 按运单粒度并行 + 失败重试。
        返回新建任务条数。
        """
        if not waybill_ids:
            return 0

        # 查重：同 (task_type, target_id=waybill) 已 pending/running 则跳过
        r = await db.execute(
            select(FreightCalcTask.target_id).where(
                FreightCalcTask.task_type == task_type,
                FreightCalcTask.target_type == "waybill",
                FreightCalcTask.target_id.in_(waybill_ids),
                FreightCalcTask.status.in_(("pending", "running")),
                FreightCalcTask.is_deleted == 0,
            )
        )
        existing_ids = {row[0] for row in r.all()}

        added = 0
        for wid in waybill_ids:
            if wid in existing_ids:
                continue
            db.add(FreightCalcTask(
                task_type=task_type,
                target_type="waybill",
                target_id=wid,
                waybill_id=wid,
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
    ) -> list[FreightCalcTask]:
        """认领一批 pending 任务。

        实现方式：先 SELECT IDs（按 priority desc, created_at asc），
        再 UPDATE ... WHERE id IN (...) AND status='pending' 锁住。
        最后再 SELECT 已认领行返回给 worker。
        """
        ids_q = await db.execute(
            select(FreightCalcTask.id).where(
                FreightCalcTask.status == "pending",
                FreightCalcTask.is_deleted == 0,
            ).order_by(
                FreightCalcTask.priority.desc(),
                FreightCalcTask.created_at.asc(),
            ).limit(batch_size)
        )
        ids = [row[0] for row in ids_q.all()]
        if not ids:
            return []

        await db.execute(
            update(FreightCalcTask)
            .where(
                FreightCalcTask.id.in_(ids),
                FreightCalcTask.status == "pending",
            )
            .values(status="running", started_at=datetime.now())
        )
        # 重新查（也只取 status='running'，避免被别的进程抢走）
        r = await db.execute(
            select(FreightCalcTask).where(
                FreightCalcTask.id.in_(ids),
                FreightCalcTask.status == "running",
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def mark_success(db: AsyncSession, task_id: int) -> None:
        await db.execute(
            update(FreightCalcTask)
            .where(FreightCalcTask.id == task_id)
            .values(
                status="success",
                finished_at=datetime.now(),
                error_message=None,
            )
        )

    @staticmethod
    async def mark_failed(
        db: AsyncSession, task_id: int, error_message: str
    ) -> None:
        """失败：未超过最大重试 → 回退 pending 等待重试；否则 failed 终态。"""
        r = await db.execute(
            select(FreightCalcTask).where(FreightCalcTask.id == task_id)
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
        waybill_id: Optional[int] = None,
    ) -> dict:
        base = select(FreightCalcTask).where(FreightCalcTask.is_deleted == 0)
        if status:
            base = base.where(FreightCalcTask.status == status)
        if task_type:
            base = base.where(FreightCalcTask.task_type == task_type)
        if waybill_id:
            base = base.where(FreightCalcTask.waybill_id == waybill_id)

        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0

        r = await db.execute(
            base.order_by(FreightCalcTask.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = []
        for t in r.scalars().all():
            items.append({
                "id": t.id,
                "taskType": t.task_type,
                "targetType": t.target_type,
                "targetId": t.target_id,
                "waybillId": t.waybill_id,
                "status": t.status,
                "priority": t.priority,
                "retryCount": t.retry_count,
                "maxRetryCount": t.max_retry_count,
                "errorMessage": t.error_message,
                "triggeredByUserId": t.triggered_by_user_id,
                "startedAt": t.started_at,
                "finishedAt": t.finished_at,
                "createdAt": t.created_at,
                "updatedAt": t.updated_at,
            })
        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def retry_task(db: AsyncSession, task_id: int) -> None:
        await db.execute(
            update(FreightCalcTask)
            .where(FreightCalcTask.id == task_id)
            .values(
                status="pending",
                retry_count=0,
                error_message=None,
                started_at=None,
                finished_at=None,
            )
        )
