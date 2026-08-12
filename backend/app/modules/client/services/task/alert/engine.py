"""
任务预警引擎

职责：把「任务事实 + 阈值配置」算成 ``biz_task_alert`` 里的一行行预警，并维护它们的
生命周期（新增 / 升级 / 自动消除）。工作台阶段卡与列表只读这张表，不再各自现算。

两条触发通道：

- ``scan_tenant``：worker 周期性全量扫描。时间流逝导致的预警只能靠它发现。
- ``recompute_tasks``：任务状态变更后即时重算单张任务，避免操作完还要等一轮扫描。

写入约定：

- 同一 ``(task_id, rule_code)`` 在未删除范围内只有一行，重复扫描是 upsert。
- **级别只升不降**：阈值调宽不会把历史的「严重」改写回「关注」。
- **人工忽略不回弹**：调度员忽略过的预警，扫描不再改写它的状态。
- 条件不再满足（推进到下一阶段 / 异常消失）时置为「已自动消除」并留 ``resolved_at``，
  这样才能统计一条预警到底挂了多久。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_alert import (
    ALERT_LEVEL_CRITICAL,
    ALERT_LEVEL_WARN,
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_AUTO_RESOLVED,
    ALERT_STATUS_DISMISSED,
    ALERT_STATUS_RESOLVED,
    TaskAlert,
)
from app.modules.client.models.task.task_alert_rule import TaskAlertRule
from app.modules.client.services.task.alert.catalog import (
    ACTIVE_STAGES,
    BASIS_ARRIVE,
    BASIS_LOAD,
    KIND_ANCHOR,
    KIND_DEADLINE,
    KIND_EXECUTION,
    KIND_STAGNANT,
    RULE_CAPACITY_ABNORMAL,
    RULE_LOAD_MISMATCH,
    RULE_NO_ROUTE_PLAN,
    RULES_BY_STAGE,
    AlertRuleDef,
)
from app.modules.client.services.task.alert.context import (
    ANCHOR_LOOKUP,
    CAPACITY_STATUS_UNAVAILABLE,
    RegionChainResolver,
    TaskAlertContext,
    TaskAlertContextLoader,
)
from app.modules.client.services.task.alert.matcher import (
    ResolvedThreshold,
    is_rule_effective,
    resolve_threshold,
)

# 单批处理任务数：控制单条 SQL 的 IN 长度与内存占用
_BATCH_SIZE = 500


@dataclass
class AlertHit:
    """一次命中判定的结果"""

    rule_code: str
    level: int
    due_at: Optional[datetime]
    overdue_minutes: int
    rule_id: Optional[int]


class TaskAlertEngine:
    """任务预警引擎"""

    # ------------------------------------------------------------------
    # 对外入口
    # ------------------------------------------------------------------

    @staticmethod
    async def scan_tenant(
        db: AsyncSession, *, now: Optional[datetime] = None
    ) -> dict:
        """全量扫描当前租户的执行中任务。"""
        moment = now or datetime.now()
        r = await db.execute(
            select(Task.id).where(
                Task.is_deleted == 0, Task.status.in_(ACTIVE_STAGES)
            )
        )
        task_ids = [int(i) for i in r.scalars().all()]

        stats = {"tasks": len(task_ids), "created": 0, "updated": 0, "resolved": 0}
        rules = await TaskAlertEngine._load_rules(db, moment.date())
        resolver = RegionChainResolver()

        for chunk in _chunks(task_ids, _BATCH_SIZE):
            part = await TaskAlertEngine._process_batch(
                db, chunk, rules=rules, now=moment, resolver=resolver
            )
            for k in ("created", "updated", "resolved"):
                stats[k] += part[k]
            await db.commit()

        # 已离开执行阶段（交车 / 关闭 / 取消 / 删除）的任务，残留预警统一收尾
        stats["resolved"] += await TaskAlertEngine._resolve_orphans(db, moment)
        await db.commit()
        return stats

    @staticmethod
    async def recompute_tasks(
        db: AsyncSession,
        task_ids: Iterable[int],
        *,
        now: Optional[datetime] = None,
        commit: bool = True,
    ) -> dict:
        """重算指定任务的预警（状态变更后的即时通道）。"""
        ids = [int(i) for i in task_ids if i]
        if not ids:
            return {"tasks": 0, "created": 0, "updated": 0, "resolved": 0}
        moment = now or datetime.now()
        rules = await TaskAlertEngine._load_rules(db, moment.date())
        resolver = RegionChainResolver()
        stats = {"tasks": len(ids), "created": 0, "updated": 0, "resolved": 0}
        for chunk in _chunks(ids, _BATCH_SIZE):
            part = await TaskAlertEngine._process_batch(
                db, chunk, rules=rules, now=moment, resolver=resolver
            )
            for k in ("created", "updated", "resolved"):
                stats[k] += part[k]
        if commit:
            await db.commit()
        else:
            await db.flush()
        return stats

    # ------------------------------------------------------------------
    # 批处理
    # ------------------------------------------------------------------

    @staticmethod
    async def _process_batch(
        db: AsyncSession,
        task_ids: list[int],
        *,
        rules: "_RuleBook",
        now: datetime,
        resolver: RegionChainResolver,
    ) -> dict:
        r = await db.execute(
            select(Task).where(Task.id.in_(task_ids), Task.is_deleted == 0)
        )
        tasks = list(r.scalars().all())

        loader = TaskAlertContextLoader(resolver)
        contexts = await loader.load(
            db, [t for t in tasks if int(t.status) in ACTIVE_STAGES]
        )

        existing = await TaskAlertEngine._load_existing(db, task_ids)

        stats = {"created": 0, "updated": 0, "resolved": 0}
        for tid in task_ids:
            ctx = contexts.get(tid)
            hits = (
                TaskAlertEngine.evaluate(ctx, rules, now) if ctx is not None else []
            )
            part = TaskAlertEngine._sync_alerts(
                db,
                task_id=tid,
                ctx=ctx,
                hits=hits,
                existing=existing.get(tid, []),
                now=now,
            )
            for k in stats:
                stats[k] += part[k]
        await db.flush()
        return stats

    # ------------------------------------------------------------------
    # 判定
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(
        ctx: TaskAlertContext, rules: "_RuleBook", now: datetime
    ) -> list[AlertHit]:
        """对单张任务跑完本阶段所有规则，返回命中的预警。"""
        hits: list[AlertHit] = []
        for rule_def in RULES_BY_STAGE.get(ctx.stage, ()):
            if rules.is_disabled(rule_def.code, ctx.stage):
                continue
            threshold = resolve_threshold(
                rule_def, ctx, ctx.stage, rules.candidates(rule_def.code)
            )
            hit = TaskAlertEngine._evaluate_one(rule_def, threshold, ctx, now)
            if hit is not None:
                hits.append(hit)
        return hits

    @staticmethod
    def _evaluate_one(
        rule_def: AlertRuleDef,
        threshold: ResolvedThreshold,
        ctx: TaskAlertContext,
        now: datetime,
    ) -> Optional[AlertHit]:
        if rule_def.kind == KIND_EXECUTION:
            if not TaskAlertEngine._execution_hit(rule_def, ctx):
                return None
            return AlertHit(
                rule_code=rule_def.code,
                level=rule_def.execution_level,
                due_at=None,
                overdue_minutes=0,
                rule_id=threshold.rule_id,
            )

        if rule_def.kind == KIND_DEADLINE:
            return TaskAlertEngine._evaluate_deadline(
                rule_def, threshold, ctx, now
            )

        due_at = TaskAlertEngine._resolve_due_at(rule_def, threshold, ctx)
        if due_at is None:
            return None

        critical_after = threshold.critical_after_minutes
        if rule_def.kind == KIND_STAGNANT:
            # 滞留类默认「到阈值转关注、再拖一倍转严重」；显式配置则以配置为准
            critical_after = critical_after or int(
                (threshold.stagnant_hours or 0) * 60
            )

        return TaskAlertEngine._hit_from_due(
            rule_def.code,
            due_at,
            threshold.warn_ahead_minutes,
            critical_after,
            now,
            threshold.rule_id,
        )

    @staticmethod
    def _evaluate_deadline(
        rule_def: AlertRuleDef,
        threshold: ResolvedThreshold,
        ctx: TaskAlertContext,
        now: datetime,
    ) -> Optional[AlertHit]:
        """内部计划、客户要求各算一遍，谁先碰到阈值听谁的。

        某一路关掉、或任务上没填对应时间，那一路跳过。两路都落空则不出警。
        """
        plan_time, required_time = TaskAlertEngine._clock_times(
            rule_def.basis, ctx
        )
        plan_hit = (
            TaskAlertEngine._hit_from_due(
                rule_def.code,
                plan_time,
                threshold.warn_ahead_minutes,
                threshold.critical_after_minutes,
                now,
                threshold.rule_id,
            )
            if threshold.plan_enabled
            else None
        )
        required_hit = (
            TaskAlertEngine._hit_from_due(
                rule_def.code,
                required_time,
                threshold.warn_ahead_required_minutes,
                threshold.critical_after_required_minutes,
                now,
                threshold.rule_id,
            )
            if threshold.required_enabled
            else None
        )
        return TaskAlertEngine._pick_hit(plan_hit, required_hit)

    @staticmethod
    def _hit_from_due(
        rule_code: str,
        due_at: Optional[datetime],
        warn_ahead: int,
        critical_after: int,
        now: datetime,
        rule_id: Optional[int],
    ) -> Optional[AlertHit]:
        if due_at is None:
            return None
        critical_at = due_at + timedelta(minutes=critical_after)
        warn_at = due_at - timedelta(minutes=warn_ahead)
        if now >= critical_at:
            level = ALERT_LEVEL_CRITICAL
        elif now >= warn_at:
            level = ALERT_LEVEL_WARN
        else:
            return None
        overdue = int(max(0, (now - due_at).total_seconds() // 60))
        return AlertHit(
            rule_code=rule_code,
            level=level,
            due_at=due_at,
            overdue_minutes=overdue,
            rule_id=rule_id,
        )

    @staticmethod
    def _pick_hit(
        a: Optional[AlertHit], b: Optional[AlertHit]
    ) -> Optional[AlertHit]:
        if a is None:
            return b
        if b is None:
            return a
        if a.level != b.level:
            return a if a.level > b.level else b
        if a.due_at and b.due_at:
            return a if a.due_at <= b.due_at else b
        return a

    @staticmethod
    def _resolve_due_at(
        rule_def: AlertRuleDef,
        threshold: ResolvedThreshold,
        ctx: TaskAlertContext,
    ) -> Optional[datetime]:
        if rule_def.kind == KIND_DEADLINE:
            plan_time, required_time = TaskAlertEngine._clock_times(
                rule_def.basis, ctx
            )
            candidates: list[datetime] = []
            if threshold.plan_enabled and plan_time is not None:
                candidates.append(plan_time)
            if threshold.required_enabled and required_time is not None:
                candidates.append(required_time)
            if not candidates:
                return None
            return min(candidates)
        if rule_def.kind == KIND_ANCHOR:
            anchor = ANCHOR_LOOKUP.get(rule_def.anchor_field or "")
            anchor_time = anchor(ctx) if anchor else None
            if anchor_time is None or threshold.anchor_offset_minutes is None:
                return None
            return anchor_time + timedelta(
                minutes=threshold.anchor_offset_minutes
            )
        if rule_def.kind == KIND_STAGNANT:
            if ctx.stage_entered_at is None or not threshold.stagnant_hours:
                return None
            return ctx.stage_entered_at + timedelta(
                hours=threshold.stagnant_hours
            )
        return None

    @staticmethod
    def _clock_times(
        basis: Optional[str], ctx: TaskAlertContext
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """返回 (内部计划时间, 客户要求时间)。客户没填则该路为 None，不回落到计划。"""
        if basis == BASIS_LOAD:
            return ctx.planned_load_time, ctx.required_load_time
        if basis == BASIS_ARRIVE:
            return ctx.planned_arrive_time, ctx.required_deliver_time
        return None, None

    @staticmethod
    def _execution_hit(rule_def: AlertRuleDef, ctx: TaskAlertContext) -> bool:
        if rule_def.code == RULE_CAPACITY_ABNORMAL:
            return ctx.capacity_operation_status in CAPACITY_STATUS_UNAVAILABLE
        if rule_def.code == RULE_LOAD_MISMATCH:
            return (
                ctx.total_quantity > 0
                and ctx.loaded_quantity < ctx.total_quantity
            )
        if rule_def.code == RULE_NO_ROUTE_PLAN:
            return ctx.dispatch_order_count == 0
        return False

    # ------------------------------------------------------------------
    # 落库
    # ------------------------------------------------------------------

    @staticmethod
    def _sync_alerts(
        db: AsyncSession,
        *,
        task_id: int,
        ctx: Optional[TaskAlertContext],
        hits: list[AlertHit],
        existing: list[TaskAlert],
        now: datetime,
    ) -> dict:
        stats = {"created": 0, "updated": 0, "resolved": 0}
        by_code = {a.rule_code: a for a in existing}
        hit_codes = {h.rule_code for h in hits}

        for hit in hits:
            row = by_code.get(hit.rule_code)
            if row is None:
                db.add(
                    TaskAlert(
                        task_id=task_id,
                        task_no=ctx.task_no if ctx else None,
                        stage=ctx.stage if ctx else 0,
                        rule_code=hit.rule_code,
                        rule_id=hit.rule_id,
                        level=hit.level,
                        status=ALERT_STATUS_ACTIVE,
                        due_at=hit.due_at,
                        overdue_minutes=hit.overdue_minutes,
                        triggered_at=now,
                        escalated_at=(
                            now if hit.level == ALERT_LEVEL_CRITICAL else None
                        ),
                        last_scan_at=now,
                        snapshot_json=ctx.snapshot() if ctx else None,
                    )
                )
                stats["created"] += 1
                continue

            if row.status == ALERT_STATUS_DISMISSED:
                # 人工忽略过的预警不回弹，否则忽略动作毫无意义
                row.last_scan_at = now
                continue
            if (
                row.status == ALERT_STATUS_RESOLVED
                and hit.level <= int(row.level)
            ):
                # 已人工处理且没有恶化，尊重处理结论；恶化了才重新拉起
                row.last_scan_at = now
                continue

            TaskAlertEngine._apply_hit(row, hit, ctx, now)
            stats["updated"] += 1

        for row in existing:
            if row.rule_code in hit_codes:
                continue
            if row.status != ALERT_STATUS_ACTIVE:
                continue
            row.status = ALERT_STATUS_AUTO_RESOLVED
            row.resolved_at = now
            row.resolve_type = "auto"
            row.last_scan_at = now
            stats["resolved"] += 1

        return stats

    @staticmethod
    def _apply_hit(
        row: TaskAlert,
        hit: AlertHit,
        ctx: Optional[TaskAlertContext],
        now: datetime,
    ) -> None:
        was_resolved = row.status != ALERT_STATUS_ACTIVE
        row.status = ALERT_STATUS_ACTIVE
        row.rule_id = hit.rule_id
        row.due_at = hit.due_at
        row.overdue_minutes = hit.overdue_minutes
        row.last_scan_at = now
        if ctx is not None:
            row.stage = ctx.stage
            row.task_no = ctx.task_no
            row.snapshot_json = ctx.snapshot()
        # 级别只升不降：阈值调宽不该改写「当时确实严重过」这个事实
        if hit.level > int(row.level):
            row.level = hit.level
            if hit.level == ALERT_LEVEL_CRITICAL and row.escalated_at is None:
                row.escalated_at = now
        if was_resolved:
            row.resolved_at = None
            row.resolved_by = None
            row.resolve_type = None

    @staticmethod
    async def _load_existing(
        db: AsyncSession, task_ids: list[int]
    ) -> dict[int, list[TaskAlert]]:
        r = await db.execute(
            select(TaskAlert).where(
                TaskAlert.task_id.in_(task_ids), TaskAlert.is_deleted == 0
            )
        )
        out: dict[int, list[TaskAlert]] = {}
        for row in r.scalars().all():
            out.setdefault(int(row.task_id), []).append(row)
        return out

    @staticmethod
    async def _resolve_orphans(db: AsyncSession, now: datetime) -> int:
        """任务已交车 / 关闭 / 取消 / 删除，但预警还挂着 —— 统一自动消除。

        正常路径下 ``_sync_alerts`` 会处理，但历史遗留与并发窗口需要这道兜底，
        否则卡片计数会挂着永远点不开的幽灵预警。
        """
        alive = select(Task.id).where(
            Task.is_deleted == 0, Task.status.in_(ACTIVE_STAGES)
        )
        r = await db.execute(
            select(TaskAlert).where(
                TaskAlert.is_deleted == 0,
                TaskAlert.status == ALERT_STATUS_ACTIVE,
                TaskAlert.task_id.notin_(alive),
            )
        )
        rows = list(r.scalars().all())
        for row in rows:
            row.status = ALERT_STATUS_AUTO_RESOLVED
            row.resolved_at = now
            row.resolve_type = "auto"
            row.last_scan_at = now
        return len(rows)

    # ------------------------------------------------------------------
    # 规则加载
    # ------------------------------------------------------------------

    @staticmethod
    async def _load_rules(db: AsyncSession, today: date) -> "_RuleBook":
        r = await db.execute(
            select(TaskAlertRule).where(TaskAlertRule.is_deleted == 0)
        )
        return _RuleBook(list(r.scalars().all()), today)


class _RuleBook:
    """一轮扫描内复用的规则快照

    规则表通常只有几十行，整表载入内存后所有任务共用，避免逐任务查库。
    """

    def __init__(self, rules: list[TaskAlertRule], today: date) -> None:
        self._by_code: dict[str, list[TaskAlertRule]] = {}
        self._disabled: set[tuple[str, Optional[int]]] = set()
        for rule in rules:
            code = rule.rule_code
            if not is_rule_effective(rule, today):
                # 「租户默认阈值」那一行被停用 = 整个规则类型对本租户关闭
                if not rule.has_scope():
                    self._disabled.add(
                        (code, int(rule.stage) if rule.stage is not None else None)
                    )
                continue
            self._by_code.setdefault(code, []).append(rule)

    def candidates(self, rule_code: str) -> list[TaskAlertRule]:
        return self._by_code.get(rule_code, [])

    def is_disabled(self, rule_code: str, stage: int) -> bool:
        return (
            (rule_code, None) in self._disabled
            or (rule_code, stage) in self._disabled
        )


def _chunks(items: list[int], size: int) -> Iterable[list[int]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]
