"""
预警阈值匹配（三层模型的第 2、3 层）

从租户配置的 ``biz_task_alert_rule`` 中，为「某张任务 + 某条规则类型」挑出唯一生效的
阈值。规则越特化得分越高，得分最高者胜出；目录内置默认值兜底。

与计费引擎（``FreightMatcher`` / ``CostMatcher``）的刻意分叉：同分冲突时**不抛异常**，
按 ``rule_version`` → ``id`` 兜底选取并继续出警。计费算错金额可以事后追回，
预警漏报却会让任务无声地烂在阶段里 —— 不能因为配置写重了就整片不报警。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from app.modules.client.models.task.task_alert_rule import (
    RULE_STATUS_ENABLED,
    TaskAlertRule,
    clocks_from_time_basis,
    time_basis_from_clocks,
)
from app.modules.client.services.task.alert.catalog import AlertRuleDef
from app.modules.client.services.task.alert.context import TaskAlertContext

# ---- 特异度分值（与 FreightMatcher 同一量级心智）----
SCORE_CUSTOMER_ID = 100_000
SCORE_CUSTOMER_TYPE = 50_000
SCORE_LINE_BASE = 30_000   # 精确到任务自身行政区
SCORE_LINE_STEP = 10_000   # 每向上一级行政区衰减
SCORE_LINE_MIN = 10_000
SCORE_DISTANCE = 8_000
SCORE_SERIES = 3_000
SCORE_BRAND = 2_000
SCORE_CARRIER_TYPE = 1_000


@dataclass
class ResolvedThreshold:
    """某任务在某规则类型上最终生效的阈值"""

    rule_id: Optional[int]
    rule_name: Optional[str]
    time_basis: int
    plan_enabled: bool
    required_enabled: bool
    anchor_offset_minutes: Optional[int]
    warn_ahead_minutes: int
    critical_after_minutes: int
    warn_ahead_required_minutes: int
    critical_after_required_minutes: int
    stagnant_hours: Optional[int]
    score: int = 0
    conflicted: bool = False


def _region_score(
    rule_region_id: Optional[int], chain: tuple[int, ...]
) -> Optional[int]:
    """规则线路端点是否落在任务行政区上溯链上；越靠近任务自身得分越高。

    返回 ``None`` 表示不匹配（该规则整条淘汰）。
    """
    if rule_region_id is None:
        return 0
    try:
        idx = chain.index(int(rule_region_id))
    except ValueError:
        return None
    return max(SCORE_LINE_MIN, SCORE_LINE_BASE - idx * SCORE_LINE_STEP)


def _match_rule(
    rule: TaskAlertRule, ctx: TaskAlertContext, stage: int
) -> Optional[int]:
    """判断规则是否适用于该任务；适用则返回特异度得分，否则 None。"""
    if rule.stage is not None and int(rule.stage) != stage:
        return None

    score = 0

    if rule.customer_id is not None:
        if int(rule.customer_id) not in ctx.customer_ids:
            return None
        score += SCORE_CUSTOMER_ID

    if rule.customer_type is not None:
        if int(rule.customer_type) not in ctx.customer_types:
            return None
        score += SCORE_CUSTOMER_TYPE

    origin_score = _region_score(rule.origin_region_id, ctx.origin_region_chain)
    if origin_score is None:
        return None
    dest_score = _region_score(
        rule.destination_region_id, ctx.destination_region_chain
    )
    if dest_score is None:
        return None
    # 单端配置的线路规则不应与双端配置同分，取两端中更粗的那一级作为线路分
    line_hits = [s for s in (origin_score, dest_score) if s > 0]
    if line_hits:
        score += min(line_hits)

    if rule.distance_min is not None or rule.distance_max is not None:
        if ctx.mileage is None:
            return None
        m = Decimal(str(ctx.mileage))
        if rule.distance_min is not None and m < Decimal(str(rule.distance_min)):
            return None
        if rule.distance_max is not None and m >= Decimal(str(rule.distance_max)):
            return None
        score += SCORE_DISTANCE

    if rule.series_id is not None:
        if int(rule.series_id) not in ctx.series_ids:
            return None
        score += SCORE_SERIES

    if rule.brand_id is not None:
        if int(rule.brand_id) not in ctx.brand_ids:
            return None
        score += SCORE_BRAND

    if rule.carrier_type is not None:
        if ctx.carrier_type != int(rule.carrier_type):
            return None
        score += SCORE_CARRIER_TYPE

    return score + int(rule.priority or 0)


def is_rule_effective(rule: TaskAlertRule, today: date) -> bool:
    """状态启用且在生效期内。"""
    if int(rule.status or 0) != RULE_STATUS_ENABLED:
        return False
    if rule.effective_date and today < rule.effective_date:
        return False
    if rule.expiry_date and today > rule.expiry_date:
        return False
    return True


def resolve_threshold(
    rule_def: AlertRuleDef,
    ctx: TaskAlertContext,
    stage: int,
    candidates: list[TaskAlertRule],
) -> ResolvedThreshold:
    """在候选规则中选出生效阈值，缺项回落目录内置默认值。"""
    best: Optional[TaskAlertRule] = None
    best_score = -1
    conflicted = False

    for rule in candidates:
        score = _match_rule(rule, ctx, stage)
        if score is None:
            continue
        if score > best_score:
            best, best_score, conflicted = rule, score, False
        elif score == best_score and best is not None:
            conflicted = True
            # 同分不阻断：版本更新者优先，其次 id 更大者
            if (int(rule.rule_version or 1), int(rule.id)) > (
                int(best.rule_version or 1), int(best.id)
            ):
                best = rule

    return _compose(rule_def, stage, best, best_score if best else 0, conflicted)


def _compose(
    rule_def: AlertRuleDef,
    stage: int,
    rule: Optional[TaskAlertRule],
    score: int,
    conflicted: bool,
) -> ResolvedThreshold:
    default_stagnant = rule_def.default_stagnant_hours.get(stage)
    if rule is None:
        return ResolvedThreshold(
            rule_id=None,
            rule_name=None,
            time_basis=rule_def.default_time_basis,
            plan_enabled=rule_def.default_plan_enabled,
            required_enabled=rule_def.default_required_enabled,
            anchor_offset_minutes=rule_def.default_anchor_offset_minutes,
            warn_ahead_minutes=rule_def.default_warn_ahead_minutes,
            critical_after_minutes=rule_def.default_critical_after_minutes,
            warn_ahead_required_minutes=rule_def.default_warn_ahead_required_minutes,
            critical_after_required_minutes=(
                rule_def.default_critical_after_required_minutes
            ),
            stagnant_hours=default_stagnant,
        )

    plan_on, req_on = _resolve_clocks(rule, rule_def)
    return ResolvedThreshold(
        rule_id=int(rule.id),
        rule_name=rule.rule_name,
        time_basis=time_basis_from_clocks(int(plan_on), int(req_on)),
        plan_enabled=bool(plan_on),
        required_enabled=bool(req_on),
        anchor_offset_minutes=(
            int(rule.anchor_offset_minutes)
            if rule.anchor_offset_minutes is not None
            else rule_def.default_anchor_offset_minutes
        ),
        warn_ahead_minutes=(
            int(rule.warn_ahead_minutes)
            if rule.warn_ahead_minutes is not None
            else rule_def.default_warn_ahead_minutes
        ),
        critical_after_minutes=(
            int(rule.critical_after_minutes)
            if rule.critical_after_minutes is not None
            else rule_def.default_critical_after_minutes
        ),
        warn_ahead_required_minutes=(
            int(rule.warn_ahead_required_minutes)
            if getattr(rule, "warn_ahead_required_minutes", None) is not None
            else rule_def.default_warn_ahead_required_minutes
        ),
        critical_after_required_minutes=(
            int(rule.critical_after_required_minutes)
            if getattr(rule, "critical_after_required_minutes", None) is not None
            else rule_def.default_critical_after_required_minutes
        ),
        stagnant_hours=(
            int(rule.stagnant_hours)
            if rule.stagnant_hours is not None
            else default_stagnant
        ),
        score=score,
        conflicted=conflicted,
    )


def _resolve_clocks(rule: TaskAlertRule, rule_def) -> tuple[int, int]:
    """优先读两路开关；老数据没这两列时按 time_basis 还原。"""
    plan = getattr(rule, "plan_enabled", None)
    required = getattr(rule, "required_enabled", None)
    if plan is None and required is None:
        basis = (
            int(rule.time_basis)
            if rule.time_basis is not None
            else rule_def.default_time_basis
        )
        return clocks_from_time_basis(basis)
    return (
        1 if (plan is None or int(plan)) else 0,
        1 if (required is None or int(required)) else 0,
    )
