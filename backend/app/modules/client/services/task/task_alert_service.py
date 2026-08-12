"""
任务预警读写 Service

引擎负责「算」，本 Service 负责「查」与「处置」：

- 工作台阶段卡的关注 / 严重计数
- 任务列表的预警子集过滤与行级标记
- 调度员的认领 / 处理 / 忽略动作

一个任务可能同时命中多条规则，对外一律按**最高级别**归类，
否则卡片上「常 + 关注 + 严重」就不等于阶段总数，调度员会立刻发现对不上。
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task_alert import (
    ALERT_LEVEL_CRITICAL,
    ALERT_LEVEL_WARN,
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_DISMISSED,
    ALERT_STATUS_RESOLVED,
    TaskAlert,
)
from app.modules.client.services.task.alert.catalog import CATALOG_BY_CODE

# 列表 alertLevel 过滤取值
LEVEL_FILTER_NORMAL = "normal"
LEVEL_FILTER_WARN = "warn"
LEVEL_FILTER_CRITICAL = "critical"
LEVEL_FILTER_ANY = "any"
VALID_LEVEL_FILTERS = (
    LEVEL_FILTER_NORMAL,
    LEVEL_FILTER_WARN,
    LEVEL_FILTER_CRITICAL,
    LEVEL_FILTER_ANY,
)


class TaskAlertService:
    """任务预警查询与处置"""

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    @staticmethod
    def active_alert_exists(task_id_column, *, level: Optional[int] = None):
        """构造「该任务存在活跃预警」的 EXISTS 子查询条件。

        供任务列表与统计复用，避免各处各写一份口径。
        """
        stmt = select(1).select_from(TaskAlert).where(
            TaskAlert.task_id == task_id_column,
            TaskAlert.is_deleted == 0,
            TaskAlert.status == ALERT_STATUS_ACTIVE,
        )
        if level is not None:
            stmt = stmt.where(TaskAlert.level == level)
        return stmt.exists()

    @staticmethod
    def overdue_minutes_expr(task_id_column):
        """该任务活跃预警中最大的超时分钟数（相关子查询，供排序用）。"""
        return (
            select(func.max(TaskAlert.overdue_minutes))
            .where(
                TaskAlert.task_id == task_id_column,
                TaskAlert.is_deleted == 0,
                TaskAlert.status == ALERT_STATUS_ACTIVE,
            )
            .correlate_except(TaskAlert)
            .scalar_subquery()
        )

    @staticmethod
    async def stage_level_counts(
        db: AsyncSession, task_id_subquery
    ) -> dict[int, dict[str, int]]:
        """按阶段统计关注 / 严重任务数（同一任务只按最高级别计一次）。

        ``task_id_subquery`` 是已应用工作台筛选的任务 ID 集合，
        保证卡片计数与列表筛选口径完全一致。
        """
        r = await db.execute(
            select(
                TaskAlert.stage,
                TaskAlert.task_id,
                func.max(TaskAlert.level),
            )
            .where(
                TaskAlert.is_deleted == 0,
                TaskAlert.status == ALERT_STATUS_ACTIVE,
                TaskAlert.task_id.in_(task_id_subquery),
            )
            .group_by(TaskAlert.stage, TaskAlert.task_id)
        )
        out: dict[int, dict[str, int]] = {}
        for stage, _task_id, top_level in r.all():
            bucket = out.setdefault(int(stage), {"warn": 0, "critical": 0})
            if int(top_level) == ALERT_LEVEL_CRITICAL:
                bucket["critical"] += 1
            else:
                bucket["warn"] += 1
        return out

    @staticmethod
    async def top_level_map(
        db: AsyncSession, task_ids: Sequence[int]
    ) -> dict[int, dict]:
        """任务 ID → {level, codes}，供列表行级渲染。"""
        ids = [int(i) for i in task_ids if i]
        if not ids:
            return {}
        r = await db.execute(
            select(
                TaskAlert.task_id,
                TaskAlert.level,
                TaskAlert.rule_code,
                TaskAlert.overdue_minutes,
            )
            .where(
                TaskAlert.task_id.in_(ids),
                TaskAlert.is_deleted == 0,
                TaskAlert.status == ALERT_STATUS_ACTIVE,
            )
            .order_by(TaskAlert.level.desc(), TaskAlert.overdue_minutes.desc())
        )
        out: dict[int, dict] = {}
        for task_id, level, code, overdue in r.all():
            entry = out.setdefault(
                int(task_id), {"level": 0, "codes": [], "overdueMinutes": 0}
            )
            entry["level"] = max(entry["level"], int(level))
            entry["overdueMinutes"] = max(
                entry["overdueMinutes"], int(overdue or 0)
            )
            entry["codes"].append(code)
        return out

    @staticmethod
    async def list_of_task(
        db: AsyncSession, task_id: int, *, active_only: bool = False
    ) -> list[TaskAlert]:
        stmt = select(TaskAlert).where(
            TaskAlert.task_id == task_id, TaskAlert.is_deleted == 0
        )
        if active_only:
            stmt = stmt.where(TaskAlert.status == ALERT_STATUS_ACTIVE)
        r = await db.execute(
            stmt.order_by(
                TaskAlert.status.asc(),
                TaskAlert.level.desc(),
                TaskAlert.triggered_at.desc(),
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def page_alerts(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        stage: Optional[int] = None,
        level: Optional[int] = None,
        status: Optional[int] = None,
        rule_code: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> tuple[list[TaskAlert], int]:
        base = select(TaskAlert).where(TaskAlert.is_deleted == 0)
        cnt = select(func.count(TaskAlert.id)).where(TaskAlert.is_deleted == 0)

        conds = []
        if stage is not None:
            conds.append(TaskAlert.stage == stage)
        if level is not None:
            conds.append(TaskAlert.level == level)
        if status is not None:
            conds.append(TaskAlert.status == status)
        if rule_code:
            conds.append(TaskAlert.rule_code == rule_code)
        if keyword and keyword.strip():
            conds.append(TaskAlert.task_no.like(f"%{keyword.strip()}%"))
        for c in conds:
            base = base.where(c)
            cnt = cnt.where(c)

        total = int((await db.execute(cnt)).scalar() or 0)
        offset = max(0, (page - 1) * page_size)
        r = await db.execute(
            base.order_by(
                TaskAlert.level.desc(),
                TaskAlert.overdue_minutes.desc(),
                TaskAlert.id.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    # ------------------------------------------------------------------
    # 处置
    # ------------------------------------------------------------------

    @staticmethod
    async def get_or_404(db: AsyncSession, alert_id: int) -> TaskAlert:
        r = await db.execute(
            select(TaskAlert).where(
                TaskAlert.id == alert_id, TaskAlert.is_deleted == 0
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这条预警不存在，可能已被处理或任务已关闭")
        return row

    @staticmethod
    async def claim(
        db: AsyncSession,
        alert_id: int,
        *,
        user_id: Optional[int],
        user_name: Optional[str],
    ) -> TaskAlert:
        row = await TaskAlertService.get_or_404(db, alert_id)
        if row.status != ALERT_STATUS_ACTIVE:
            raise BizException("这条预警已经处理完了，无需再认领")
        row.handler_id = user_id
        row.handler_name = user_name
        row.claimed_at = datetime.now()
        await db.flush()
        return row

    @staticmethod
    async def resolve(
        db: AsyncSession,
        alert_id: int,
        *,
        user_id: Optional[int],
        remark: Optional[str] = None,
    ) -> TaskAlert:
        row = await TaskAlertService.get_or_404(db, alert_id)
        if row.status != ALERT_STATUS_ACTIVE:
            raise BizException("这条预警已经处理完了，无需重复操作")
        row.status = ALERT_STATUS_RESOLVED
        row.resolve_type = "manual"
        row.resolved_at = datetime.now()
        row.resolved_by = user_id
        row.resolve_remark = _trim(remark)
        await db.flush()
        return row

    @staticmethod
    async def dismiss(
        db: AsyncSession,
        alert_id: int,
        *,
        user_id: Optional[int],
        reason: str,
    ) -> TaskAlert:
        text = _trim(reason)
        if not text:
            raise BizException("请填写忽略原因，便于后续复盘")
        row = await TaskAlertService.get_or_404(db, alert_id)
        if row.status != ALERT_STATUS_ACTIVE:
            raise BizException("这条预警已经处理完了，无需再忽略")
        row.status = ALERT_STATUS_DISMISSED
        row.resolve_type = "dismiss"
        row.resolved_at = datetime.now()
        row.resolved_by = user_id
        row.resolve_remark = text
        await db.flush()
        return row

    @staticmethod
    async def batch_dismiss(
        db: AsyncSession,
        alert_ids: Iterable[int],
        *,
        user_id: Optional[int],
        reason: str,
    ) -> dict:
        text = _trim(reason)
        if not text:
            raise BizException("请填写忽略原因，便于后续复盘")
        ids = [int(i) for i in alert_ids if i]
        if not ids:
            raise BizException("请选择要忽略的预警")
        r = await db.execute(
            select(TaskAlert).where(
                TaskAlert.id.in_(ids),
                TaskAlert.is_deleted == 0,
                TaskAlert.status == ALERT_STATUS_ACTIVE,
            )
        )
        rows = list(r.scalars().all())
        now = datetime.now()
        for row in rows:
            row.status = ALERT_STATUS_DISMISSED
            row.resolve_type = "dismiss"
            row.resolved_at = now
            row.resolved_by = user_id
            row.resolve_remark = text
        await db.flush()
        return {"success": len(rows), "skipped": len(ids) - len(rows)}

    @staticmethod
    async def dismiss_by_tasks(
        db: AsyncSession,
        task_ids: Iterable[int],
        *,
        user_id: Optional[int],
        reason: str,
    ) -> dict:
        """按任务批量忽略其全部活跃预警（工作台批量操作用）。"""
        text = _trim(reason)
        if not text:
            raise BizException("请填写忽略原因，便于后续复盘")
        ids = [int(i) for i in task_ids if i]
        if not ids:
            raise BizException("请选择要忽略预警的任务")
        r = await db.execute(
            select(TaskAlert).where(
                TaskAlert.task_id.in_(ids),
                TaskAlert.is_deleted == 0,
                TaskAlert.status == ALERT_STATUS_ACTIVE,
            )
        )
        rows = list(r.scalars().all())
        now = datetime.now()
        for row in rows:
            row.status = ALERT_STATUS_DISMISSED
            row.resolve_type = "dismiss"
            row.resolved_at = now
            row.resolved_by = user_id
            row.resolve_remark = text
        await db.flush()
        return {"success": len(rows), "tasks": len(ids)}


def rule_label(rule_code: str) -> str:
    rule_def = CATALOG_BY_CODE.get(rule_code)
    return rule_def.name if rule_def else rule_code


def _trim(v: Optional[str]) -> Optional[str]:
    return v.strip()[:255] if v and v.strip() else None


__all__ = [
    "TaskAlertService",
    "rule_label",
    "LEVEL_FILTER_NORMAL",
    "LEVEL_FILTER_WARN",
    "LEVEL_FILTER_CRITICAL",
    "LEVEL_FILTER_ANY",
    "VALID_LEVEL_FILTERS",
    "ALERT_LEVEL_WARN",
    "ALERT_LEVEL_CRITICAL",
]
