"""运营调度 · 任务预警引擎（纯逻辑，零 DB）测试

覆盖预警体系里「算错了会直接坑到调度员」的几处判定：

- 阈值命中：关注 / 严重的时间边界
- 黄转红：级别只升不降，且 ``escalated_at`` 只记第一次升级
- 跨阶段自动消除：条件不再满足时置为「已自动消除」而不是留在卡片上
- 多规则同分：不抛异常、不漏报，按版本号兜底选一条
- 类型级开关：默认那一行停用即整类关闭
- 时间基准：客户要求时间与内部计划时间取更早

对应需求：doc/02.需求文档/02.企业端/06.运营调度模块/04.任务预警体系设计.md
对应代码：backend/app/modules/client/services/task/alert/**
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from app.modules.client.models.task.task_alert import (
    ALERT_LEVEL_CRITICAL,
    ALERT_LEVEL_WARN,
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_AUTO_RESOLVED,
    ALERT_STATUS_DISMISSED,
    TaskAlert,
)
from app.modules.client.models.task.task_alert_rule import (
    TIME_BASIS_PLAN,
    TaskAlertRule,
)
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_PENDING_DISPATCH,
)
from app.modules.client.services.task.alert.catalog import (
    CATALOG_BY_CODE,
    RULE_ARRIVE_TIMEOUT,
    RULE_DISPATCH_TIMEOUT,
    RULE_LOAD_TIMEOUT,
    RULE_STAGE_STAGNANT,
)
from app.modules.client.services.task.alert.context import TaskAlertContext
from app.modules.client.services.task.alert.engine import (
    AlertHit,
    TaskAlertEngine,
    _RuleBook,
)
from app.modules.client.services.task.alert.matcher import resolve_threshold

NOW = datetime(2026, 8, 12, 12, 0, 0)
TODAY = NOW.date()


def _ctx(stage: int = TASK_PENDING_DISPATCH, **kwargs) -> TaskAlertContext:
    base = dict(task_id=1, task_no="RW0001", stage=stage)
    base.update(kwargs)
    return TaskAlertContext(**base)


def _rule(**kwargs) -> TaskAlertRule:
    """构造一条未落库的规则行（id 必须给，匹配器要用它做 tie-break）。"""
    rule = TaskAlertRule(**kwargs)
    rule.is_deleted = 0
    rule.priority = kwargs.get("priority", 0)
    rule.status = kwargs.get("status", 1)
    rule.rule_version = kwargs.get("rule_version", 1)
    return rule


class TestThresholdHit:
    """待派车超时：默认提前 180 分钟关注，一超时即严重"""

    def _hit(self, planned_load_time):
        ctx = _ctx(planned_load_time=planned_load_time)
        book = _RuleBook([], TODAY)
        hits = TaskAlertEngine.evaluate(ctx, book, NOW)
        return {h.rule_code: h for h in hits}

    def test_still_far_from_deadline_is_quiet(self):
        # 距计划装车还有 5 小时 > 默认 3 小时提前量，不该打扰调度员
        assert RULE_DISPATCH_TIMEOUT not in self._hit(NOW + timedelta(hours=5))

    def test_inside_warn_window_is_warn(self):
        hit = self._hit(NOW + timedelta(hours=2))[RULE_DISPATCH_TIMEOUT]
        assert hit.level == ALERT_LEVEL_WARN
        assert hit.overdue_minutes == 0

    def test_past_deadline_is_critical(self):
        hit = self._hit(NOW - timedelta(minutes=90))[RULE_DISPATCH_TIMEOUT]
        assert hit.level == ALERT_LEVEL_CRITICAL
        assert hit.overdue_minutes == 90

    def test_warn_boundary_is_inclusive(self):
        # 恰好踩在提前量边界上要出警，否则「提前 3 小时提醒」名不副实
        hit = self._hit(NOW + timedelta(minutes=180))[RULE_DISPATCH_TIMEOUT]
        assert hit.level == ALERT_LEVEL_WARN

    def test_load_stage_keeps_elastic_window_before_critical(self):
        """待装车留了 1 小时弹性：刚超时算关注，超过 1 小时才算严重。"""
        ctx = _ctx(stage=TASK_DISPATCHED, planned_load_time=NOW - timedelta(minutes=30))
        book = _RuleBook([], TODAY)
        hits = {h.rule_code: h for h in TaskAlertEngine.evaluate(ctx, book, NOW)}
        assert hits[RULE_LOAD_TIMEOUT].level == ALERT_LEVEL_WARN

        ctx = _ctx(stage=TASK_DISPATCHED, planned_load_time=NOW - timedelta(minutes=90))
        hits = {h.rule_code: h for h in TaskAlertEngine.evaluate(ctx, book, NOW)}
        assert hits[RULE_LOAD_TIMEOUT].level == ALERT_LEVEL_CRITICAL

    def test_missing_planned_time_falls_back_to_stagnant(self):
        """没有计划时间时时效类无从判断，靠滞留类兜底，不能整片静默。"""
        ctx = _ctx(stage=TASK_DISPATCHED, stage_entered_at=NOW - timedelta(hours=30))
        book = _RuleBook([], TODAY)
        codes = {h.rule_code for h in TaskAlertEngine.evaluate(ctx, book, NOW)}
        assert RULE_LOAD_TIMEOUT not in codes
        assert RULE_STAGE_STAGNANT in codes


class TestDualClock:
    """时效类两路时钟：内部计划、客户要求各有阈值，谁先碰到听谁的。"""

    def _hit(self, **ctx_kwargs):
        ctx = _ctx(stage=TASK_ON_WAY, **ctx_kwargs)
        book = _RuleBook([], TODAY)
        hits = {h.rule_code: h for h in TaskAlertEngine.evaluate(ctx, book, NOW)}
        return hits.get(RULE_ARRIVE_TIMEOUT)

    def test_only_plan_time_uses_plan_threshold(self):
        # 目录默认内部提前 240 分钟；只有计划时间时应按内部这一路
        hit = self._hit(planned_arrive_time=NOW + timedelta(minutes=180))
        assert hit is not None
        assert hit.level == ALERT_LEVEL_WARN
        assert hit.due_at == NOW + timedelta(minutes=180)

    def test_missing_required_time_skips_that_clock(self):
        # 客户没填要求时间，客户这一路跳过，不回落到计划
        hit = self._hit(planned_arrive_time=NOW + timedelta(hours=10))
        assert hit is None

    def test_required_clock_can_fire_earlier_with_looser_due(self):
        """客户截止更晚，但提前量更大时，客户这一路会先亮。"""
        rule_def = CATALOG_BY_CODE[RULE_ARRIVE_TIMEOUT]
        ctx = _ctx(
            stage=TASK_ON_WAY,
            planned_arrive_time=NOW + timedelta(hours=4),
            required_deliver_time=NOW + timedelta(hours=6),
        )
        threshold = resolve_threshold(rule_def, ctx, ctx.stage, [])
        threshold.plan_enabled = True
        threshold.required_enabled = True
        threshold.warn_ahead_minutes = 60
        threshold.critical_after_minutes = 0
        threshold.warn_ahead_required_minutes = 420
        threshold.critical_after_required_minutes = 0
        hit = TaskAlertEngine._evaluate_one(rule_def, threshold, ctx, NOW)
        assert hit is not None
        assert hit.level == ALERT_LEVEL_WARN
        # 客户 6h 后到期、提前 7 小时 → 已经进入关注；内部 4h 后到期、提前 60 分钟还没到
        assert hit.due_at == ctx.required_deliver_time

    def test_higher_level_wins_across_clocks(self):
        rule_def = CATALOG_BY_CODE[RULE_ARRIVE_TIMEOUT]
        ctx = _ctx(
            stage=TASK_ON_WAY,
            planned_arrive_time=NOW - timedelta(minutes=10),
            required_deliver_time=NOW + timedelta(minutes=30),
        )
        threshold = resolve_threshold(rule_def, ctx, ctx.stage, [])
        threshold.plan_enabled = True
        threshold.required_enabled = True
        threshold.warn_ahead_minutes = 60
        threshold.critical_after_minutes = 0
        threshold.warn_ahead_required_minutes = 120
        threshold.critical_after_required_minutes = 0
        hit = TaskAlertEngine._evaluate_one(rule_def, threshold, ctx, NOW)
        assert hit is not None
        assert hit.level == ALERT_LEVEL_CRITICAL
        assert hit.due_at == ctx.planned_arrive_time

    def test_disabled_plan_clock_ignores_internal_time(self):
        rule_def = CATALOG_BY_CODE[RULE_ARRIVE_TIMEOUT]
        ctx = _ctx(
            stage=TASK_ON_WAY,
            planned_arrive_time=NOW - timedelta(hours=2),
            required_deliver_time=NOW + timedelta(hours=10),
        )
        threshold = resolve_threshold(rule_def, ctx, ctx.stage, [])
        threshold.plan_enabled = False
        threshold.required_enabled = True
        threshold.warn_ahead_required_minutes = 60
        threshold.critical_after_required_minutes = 0
        hit = TaskAlertEngine._evaluate_one(rule_def, threshold, ctx, NOW)
        assert hit is None

    def test_required_only_does_not_fall_back_to_plan(self):
        rule_def = CATALOG_BY_CODE[RULE_ARRIVE_TIMEOUT]
        ctx = _ctx(
            stage=TASK_ON_WAY,
            planned_arrive_time=NOW - timedelta(hours=2),
            required_deliver_time=None,
        )
        threshold = resolve_threshold(rule_def, ctx, ctx.stage, [])
        threshold.plan_enabled = False
        threshold.required_enabled = True
        hit = TaskAlertEngine._evaluate_one(rule_def, threshold, ctx, NOW)
        assert hit is None

    def test_legacy_time_basis_plan_disables_required_clock(self):
        rule = _rule(
            id=40,
            rule_code=RULE_ARRIVE_TIMEOUT,
            time_basis=TIME_BASIS_PLAN,
            warn_ahead_minutes=60,
            critical_after_minutes=0,
        )
        ctx = _ctx(
            stage=TASK_ON_WAY,
            planned_arrive_time=NOW + timedelta(hours=10),
            required_deliver_time=NOW + timedelta(minutes=10),
        )
        resolved = resolve_threshold(
            CATALOG_BY_CODE[RULE_ARRIVE_TIMEOUT], ctx, ctx.stage, [rule]
        )
        assert resolved.plan_enabled is True
        assert resolved.required_enabled is False


class TestRuleMatching:
    def test_more_specific_rule_wins(self):
        rule_def = CATALOG_BY_CODE[RULE_DISPATCH_TIMEOUT]
        loose = _rule(
            id=1, rule_code=RULE_DISPATCH_TIMEOUT, carrier_type=1,
            warn_ahead_minutes=60, critical_after_minutes=0,
        )
        tight = _rule(
            id=2, rule_code=RULE_DISPATCH_TIMEOUT, customer_id=88,
            warn_ahead_minutes=600, critical_after_minutes=0,
        )
        ctx = _ctx(carrier_type=1, customer_ids=frozenset({88}))

        resolved = resolve_threshold(rule_def, ctx, ctx.stage, [loose, tight])
        assert resolved.rule_id == 2
        assert resolved.warn_ahead_minutes == 600

    def test_non_matching_scope_is_excluded(self):
        rule_def = CATALOG_BY_CODE[RULE_DISPATCH_TIMEOUT]
        other_customer = _rule(
            id=3, rule_code=RULE_DISPATCH_TIMEOUT, customer_id=99,
            warn_ahead_minutes=600,
        )
        ctx = _ctx(customer_ids=frozenset({88}))

        resolved = resolve_threshold(rule_def, ctx, ctx.stage, [other_customer])
        assert resolved.rule_id is None
        assert resolved.warn_ahead_minutes == rule_def.default_warn_ahead_minutes

    def test_tie_does_not_block_alerting(self):
        """同分冲突只做标记，仍然出警 —— 漏报比误报严重得多。"""
        rule_def = CATALOG_BY_CODE[RULE_DISPATCH_TIMEOUT]
        a = _rule(
            id=10, rule_code=RULE_DISPATCH_TIMEOUT, customer_id=88,
            warn_ahead_minutes=100, rule_version=1,
        )
        b = _rule(
            id=11, rule_code=RULE_DISPATCH_TIMEOUT, customer_id=88,
            warn_ahead_minutes=200, rule_version=3,
        )
        ctx = _ctx(customer_ids=frozenset({88}))

        resolved = resolve_threshold(rule_def, ctx, ctx.stage, [a, b])
        assert resolved.conflicted is True
        # 版本号更大的胜出，结果稳定可预期
        assert resolved.rule_id == 11
        assert resolved.warn_ahead_minutes == 200

    def test_unset_fields_fall_back_to_catalog_defaults(self):
        rule_def = CATALOG_BY_CODE[RULE_DISPATCH_TIMEOUT]
        partial = _rule(
            id=20, rule_code=RULE_DISPATCH_TIMEOUT, carrier_type=1,
            warn_ahead_minutes=None, critical_after_minutes=45,
        )
        ctx = _ctx(carrier_type=1)

        resolved = resolve_threshold(rule_def, ctx, ctx.stage, [partial])
        assert resolved.warn_ahead_minutes == rule_def.default_warn_ahead_minutes
        assert resolved.critical_after_minutes == 45


class TestRuleBookSwitch:
    def test_disabling_the_default_row_turns_off_the_whole_type(self):
        disabled = _rule(id=30, rule_code=RULE_DISPATCH_TIMEOUT, status=0)
        book = _RuleBook([disabled], TODAY)
        ctx = _ctx(planned_load_time=NOW - timedelta(hours=3))

        codes = {h.rule_code for h in TaskAlertEngine.evaluate(ctx, book, NOW)}
        assert RULE_DISPATCH_TIMEOUT not in codes

    def test_disabling_a_scoped_rule_only_drops_that_rule(self):
        """带范围的规则被停用只是少一条候选，不影响该类型继续按默认阈值出警。"""
        scoped = _rule(
            id=31, rule_code=RULE_DISPATCH_TIMEOUT, customer_id=88, status=0
        )
        book = _RuleBook([scoped], TODAY)
        ctx = _ctx(
            planned_load_time=NOW - timedelta(hours=3),
            customer_ids=frozenset({88}),
        )

        codes = {h.rule_code for h in TaskAlertEngine.evaluate(ctx, book, NOW)}
        assert RULE_DISPATCH_TIMEOUT in codes

    def test_expired_rule_is_not_a_candidate(self):
        expired = _rule(
            id=32, rule_code=RULE_DISPATCH_TIMEOUT, customer_id=88,
            warn_ahead_minutes=600,
            effective_date=date(2020, 1, 1), expiry_date=date(2020, 12, 31),
        )
        book = _RuleBook([expired], TODAY)
        assert book.candidates(RULE_DISPATCH_TIMEOUT) == []


class TestAlertLifecycle:
    def _alert(self, **kwargs) -> TaskAlert:
        row = TaskAlert(
            task_id=1,
            task_no="RW0001",
            stage=TASK_PENDING_DISPATCH,
            rule_code=RULE_DISPATCH_TIMEOUT,
            level=ALERT_LEVEL_WARN,
            status=ALERT_STATUS_ACTIVE,
            overdue_minutes=0,
        )
        for k, v in kwargs.items():
            setattr(row, k, v)
        row.is_deleted = 0
        return row

    def test_warn_escalates_to_critical_once(self):
        row = self._alert()
        first = NOW
        TaskAlertEngine._apply_hit(
            row,
            AlertHit(RULE_DISPATCH_TIMEOUT, ALERT_LEVEL_CRITICAL, NOW, 30, None),
            None,
            first,
        )
        assert row.level == ALERT_LEVEL_CRITICAL
        assert row.escalated_at == first

        # 再扫一轮仍是严重，升级时间不该被刷新成最后一次扫描时间
        TaskAlertEngine._apply_hit(
            row,
            AlertHit(RULE_DISPATCH_TIMEOUT, ALERT_LEVEL_CRITICAL, NOW, 90, None),
            None,
            first + timedelta(hours=1),
        )
        assert row.escalated_at == first
        assert row.overdue_minutes == 90

    def test_level_never_downgrades(self):
        """阈值调宽不该改写「当时确实严重过」这个事实。"""
        row = self._alert(level=ALERT_LEVEL_CRITICAL, escalated_at=NOW)
        TaskAlertEngine._apply_hit(
            row,
            AlertHit(RULE_DISPATCH_TIMEOUT, ALERT_LEVEL_WARN, NOW, 0, None),
            None,
            NOW,
        )
        assert row.level == ALERT_LEVEL_CRITICAL

    def test_alert_auto_resolves_when_task_moves_on(self):
        """任务推进到下一阶段后，上一阶段的预警要消掉而不是留在卡片上。"""
        stale = self._alert()
        ctx = _ctx(stage=TASK_LOADED)
        stats = TaskAlertEngine._sync_alerts(
            _FakeSession(), task_id=1, ctx=ctx, hits=[], existing=[stale], now=NOW
        )
        assert stale.status == ALERT_STATUS_AUTO_RESOLVED
        assert stale.resolved_at == NOW
        assert stale.resolve_type == "auto"
        assert stats["resolved"] == 1

    def test_dismissed_alert_does_not_bounce_back(self):
        """人工忽略过的预警不回弹，否则「忽略」这个动作毫无意义。"""
        dismissed = self._alert(status=ALERT_STATUS_DISMISSED)
        hit = AlertHit(RULE_DISPATCH_TIMEOUT, ALERT_LEVEL_CRITICAL, NOW, 120, None)
        TaskAlertEngine._sync_alerts(
            _FakeSession(),
            task_id=1,
            ctx=_ctx(),
            hits=[hit],
            existing=[dismissed],
            now=NOW,
        )
        assert dismissed.status == ALERT_STATUS_DISMISSED

    def test_new_hit_creates_a_row(self):
        session = _FakeSession()
        hit = AlertHit(RULE_DISPATCH_TIMEOUT, ALERT_LEVEL_CRITICAL, NOW, 10, None)
        stats = TaskAlertEngine._sync_alerts(
            session, task_id=1, ctx=_ctx(), hits=[hit], existing=[], now=NOW
        )
        assert stats["created"] == 1
        created = session.added[0]
        assert created.rule_code == RULE_DISPATCH_TIMEOUT
        assert created.level == ALERT_LEVEL_CRITICAL
        # 建的时候就是严重，升级时间要一并落下，不然统计不出「多久转红」
        assert created.escalated_at == NOW


class _FakeSession:
    """只接住 ``db.add``：``_sync_alerts`` 是同步方法，不需要真会话。"""

    def __init__(self) -> None:
        self.added: list = []

    def add(self, obj) -> None:
        self.added.append(obj)
