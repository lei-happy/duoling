"""
任务预警规则类型目录（阈值三层模型的第 1 层：内置默认值）

这里定义「有哪些预警规则、各自盯的是哪个阶段、判定基准是什么、开箱默认阈值多少」。
配置表 ``biz_task_alert_rule`` 只负责覆盖本目录的默认值，不能凭空造出新规则类型 ——
规则的判定逻辑写在引擎里，凭空造类型没有对应的求值代码。

三类规则的判定形态不同：

- **deadline（时效-截止型）**：内部计划时间、客户要求时间各有一套阈值，
  开着的那几路分别对照各自的截止时间；谁先碰到阈值听谁的。某一路关掉、
  或任务上没填对应时间，那一路跳过。
- **anchor（时效-锚点型）**：没有外部承诺，只有「上一动作发生后允许拖多久」，
  ``due_at = 锚点时间 + anchor_offset_minutes``。装完车不发车、到场不交车属于此类。
- **stagnant（滞留型）**：只看在本阶段待了多久，与任何计划时间无关，
  是计划时间缺失时的唯一兜底。
- **execution（执行异常型）**：与时间无关的状态冲突，命中即出警。

统一判定（前三类）：

    时效类：内部计划、客户要求各算一遍，谁先碰到阈值听谁的
    其余：now >= due_at + critical_after_minutes  → 严重
          now >= due_at - warn_ahead_minutes      → 关注
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.modules.client.models.task.task_alert import (
    ALERT_LEVEL_CRITICAL,
    ALERT_LEVEL_WARN,
)
from app.modules.client.models.task.task_alert_rule import TIME_BASIS_EARLIEST
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_ARRIVED,
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_PENDING_ASSIGN,
    TASK_PENDING_DISPATCH,
)

# ---- 规则码 ----
RULE_ASSIGN_TIMEOUT = "ASSIGN_TIMEOUT"
RULE_DISPATCH_TIMEOUT = "DISPATCH_TIMEOUT"
RULE_LOAD_TIMEOUT = "LOAD_TIMEOUT"
RULE_DEPART_TIMEOUT = "DEPART_TIMEOUT"
RULE_ARRIVE_TIMEOUT = "ARRIVE_TIMEOUT"
RULE_DELIVER_TIMEOUT = "DELIVER_TIMEOUT"
RULE_STAGE_STAGNANT = "STAGE_STAGNANT"
RULE_CAPACITY_ABNORMAL = "CAPACITY_ABNORMAL"
RULE_LOAD_MISMATCH = "LOAD_MISMATCH"
RULE_NO_ROUTE_PLAN = "NO_ROUTE_PLAN"

# ---- 判定形态 ----
KIND_DEADLINE = "deadline"
KIND_ANCHOR = "anchor"
KIND_STAGNANT = "stagnant"
KIND_EXECUTION = "execution"

# ---- 基准时间字段（deadline / anchor 类用）----
BASIS_LOAD = "load"      # 装车侧：计划装车时间 / 客户要求装车时间
BASIS_ARRIVE = "arrive"  # 到货侧：计划到达时间 / 客户要求送达时间
ANCHOR_ACTUAL_LOAD = "actual_load_time"
ANCHOR_ACTUAL_ARRIVE = "actual_arrive_time"

# 调度工作台六个执行中阶段（已交车/已关闭/已取消不再预警）
ACTIVE_STAGES: tuple[int, ...] = (
    TASK_PENDING_ASSIGN,
    TASK_PENDING_DISPATCH,
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_ARRIVED,
)

STAGE_LABELS: dict[int, str] = {
    TASK_PENDING_ASSIGN: "待分配",
    TASK_PENDING_DISPATCH: "待派车",
    TASK_DISPATCHED: "待装车",
    TASK_LOADED: "待发车",
    TASK_ON_WAY: "在途",
    TASK_ARRIVED: "待交车",
}


@dataclass(frozen=True)
class AlertRuleDef:
    """一种预警规则类型的静态定义"""

    code: str
    name: str
    kind: str
    stages: tuple[int, ...]
    description: str
    # deadline / anchor 类
    basis: Optional[str] = None
    anchor_field: Optional[str] = None
    default_time_basis: int = TIME_BASIS_EARLIEST
    default_plan_enabled: bool = True
    default_required_enabled: bool = True
    default_anchor_offset_minutes: Optional[int] = None
    default_warn_ahead_minutes: int = 0
    default_critical_after_minutes: int = 0
    default_warn_ahead_required_minutes: int = 0
    default_critical_after_required_minutes: int = 0
    # stagnant 类：各阶段默认滞留小时数
    default_stagnant_hours: dict[int, int] = field(default_factory=dict)
    # execution 类：命中即出该级别
    execution_level: int = ALERT_LEVEL_CRITICAL

    @property
    def supports_time_basis(self) -> bool:
        return self.kind == KIND_DEADLINE

    @property
    def stage_scoped(self) -> bool:
        """是否需要逐阶段配置阈值（仅滞留类）。"""
        return self.kind == KIND_STAGNANT


ALERT_RULE_CATALOG: tuple[AlertRuleDef, ...] = (
    AlertRuleDef(
        code=RULE_ASSIGN_TIMEOUT,
        name="待分配超时",
        kind=KIND_DEADLINE,
        stages=(TASK_PENDING_ASSIGN,),
        description="临近装车时间仍未确认承运方",
        basis=BASIS_LOAD,
        default_warn_ahead_minutes=240,
        default_critical_after_minutes=0,
        default_warn_ahead_required_minutes=120,
        default_critical_after_required_minutes=0,
    ),
    AlertRuleDef(
        code=RULE_DISPATCH_TIMEOUT,
        name="待派车超时",
        kind=KIND_DEADLINE,
        stages=(TASK_PENDING_DISPATCH,),
        description="临近装车时间仍未派车",
        basis=BASIS_LOAD,
        default_warn_ahead_minutes=180,
        default_critical_after_minutes=0,
        default_warn_ahead_required_minutes=90,
        default_critical_after_required_minutes=0,
    ),
    AlertRuleDef(
        code=RULE_LOAD_TIMEOUT,
        name="待装车超时",
        kind=KIND_DEADLINE,
        stages=(TASK_DISPATCHED,),
        description="已派车但未按时装车",
        basis=BASIS_LOAD,
        default_warn_ahead_minutes=60,
        # 现场装车排队是常态，给 1 小时弹性再判严重，避免红标刷屏
        default_critical_after_minutes=60,
        default_warn_ahead_required_minutes=30,
        default_critical_after_required_minutes=60,
    ),
    AlertRuleDef(
        code=RULE_DEPART_TIMEOUT,
        name="装车后滞留未发车",
        kind=KIND_ANCHOR,
        stages=(TASK_LOADED,),
        description="装车完成后长时间压在场内未发车",
        anchor_field=ANCHOR_ACTUAL_LOAD,
        default_anchor_offset_minutes=120,
        default_warn_ahead_minutes=30,
        default_critical_after_minutes=60,
    ),
    AlertRuleDef(
        code=RULE_ARRIVE_TIMEOUT,
        name="到货超时",
        kind=KIND_DEADLINE,
        stages=(TASK_ON_WAY,),
        description="临近或超过承诺到货时间仍未到达",
        basis=BASIS_ARRIVE,
        default_warn_ahead_minutes=240,
        default_critical_after_minutes=0,
        default_warn_ahead_required_minutes=120,
        default_critical_after_required_minutes=0,
    ),
    AlertRuleDef(
        code=RULE_DELIVER_TIMEOUT,
        name="到场后交车超时",
        kind=KIND_ANCHOR,
        stages=(TASK_ARRIVED,),
        description="到达目的地后长时间未完成逐台交接",
        anchor_field=ANCHOR_ACTUAL_ARRIVE,
        default_anchor_offset_minutes=240,
        default_warn_ahead_minutes=60,
        default_critical_after_minutes=120,
    ),
    AlertRuleDef(
        code=RULE_STAGE_STAGNANT,
        name="阶段滞留",
        kind=KIND_STAGNANT,
        stages=ACTIVE_STAGES,
        description="任务在本阶段停留过久、进度不推进（计划时间缺失时的兜底）",
        # 与改造前前端 stageAlertHours 对齐，保证观感连续
        default_stagnant_hours={
            TASK_PENDING_ASSIGN: 12,
            TASK_PENDING_DISPATCH: 12,
            TASK_DISPATCHED: 24,
            TASK_LOADED: 6,
            TASK_ON_WAY: 48,
            TASK_ARRIVED: 24,
        },
    ),
    AlertRuleDef(
        code=RULE_CAPACITY_ABNORMAL,
        name="承运运力状态异常",
        kind=KIND_EXECUTION,
        stages=(TASK_DISPATCHED, TASK_LOADED, TASK_ON_WAY),
        description="任务执行中，但绑定运力处于休假 / 停运 / 维修保养",
        # 运力状态可能只是尚未同步，先给关注级，避免误判成硬故障
        execution_level=ALERT_LEVEL_WARN,
    ),
    AlertRuleDef(
        code=RULE_LOAD_MISMATCH,
        name="装车台数不符",
        kind=KIND_EXECUTION,
        stages=(TASK_LOADED,),
        description="已装车台数少于任务计划台数，存在漏装",
        execution_level=ALERT_LEVEL_CRITICAL,
    ),
    AlertRuleDef(
        code=RULE_NO_ROUTE_PLAN,
        name="未规划运输路线",
        kind=KIND_EXECUTION,
        stages=(TASK_DISPATCHED,),
        description="已派车但尚未规划运输路线，司机无法接单执行",
        execution_level=ALERT_LEVEL_CRITICAL,
    ),
)

CATALOG_BY_CODE: dict[str, AlertRuleDef] = {d.code: d for d in ALERT_RULE_CATALOG}

# 阶段 → 该阶段需要评估的规则定义
RULES_BY_STAGE: dict[int, tuple[AlertRuleDef, ...]] = {
    stage: tuple(d for d in ALERT_RULE_CATALOG if stage in d.stages)
    for stage in ACTIVE_STAGES
}


def catalog_payload() -> list[dict]:
    """规则类型目录（供配置页渲染默认值与可配项）。"""
    out: list[dict] = []
    for d in ALERT_RULE_CATALOG:
        out.append({
            "ruleCode": d.code,
            "ruleName": d.name,
            "kind": d.kind,
            "description": d.description,
            "stages": list(d.stages),
            "stageScoped": d.stage_scoped,
            "supportsTimeBasis": d.supports_time_basis,
            "defaults": {
                "timeBasis": d.default_time_basis,
                "planEnabled": d.default_plan_enabled,
                "requiredEnabled": d.default_required_enabled,
                "anchorOffsetMinutes": d.default_anchor_offset_minutes,
                "warnAheadMinutes": d.default_warn_ahead_minutes,
                "criticalAfterMinutes": d.default_critical_after_minutes,
                "warnAheadRequiredMinutes": d.default_warn_ahead_required_minutes,
                "criticalAfterRequiredMinutes": d.default_critical_after_required_minutes,
                "stagnantHours": dict(d.default_stagnant_hours) or None,
            },
        })
    return out
