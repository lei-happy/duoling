"""
任务预警实例表（租户库）

由 ``TaskAlertEngine`` 周期性扫描 + 状态变更即时触发写入，是调度工作台
阶段卡「关注 / 严重」计数与列表行级标记的唯一数据来源。

一条预警 = 某张任务单在某条规则（``rule_code``）上的最新命中状态。
同一任务同一规则在「未删除」范围内只保留一条，扫描时 upsert；
条件不再满足（任务推进到下一阶段 / 阈值调宽）时由引擎置为「自动消除」。

人工「已忽略」的记录扫描不再覆盖其状态 —— 否则调度员刚忽略，
下一轮扫描又把它弹回活跃，预警会变成噪音。
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    Index,
    Integer,
    SmallInteger,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase

# ---- 预警级别（只升不降：阈值调整不应改写历史事实）----
ALERT_LEVEL_WARN = 1      # 关注（黄）：距应完成时间进入提前量窗口
ALERT_LEVEL_CRITICAL = 2  # 严重（红）：已超时，或执行异常类直接命中

ALERT_LEVEL_LABELS: dict[int, str] = {
    ALERT_LEVEL_WARN: "关注",
    ALERT_LEVEL_CRITICAL: "严重",
}

# ---- 处理状态 ----
ALERT_STATUS_ACTIVE = 0        # 活跃（含已认领，认领只写 handler 不改 status）
ALERT_STATUS_RESOLVED = 1      # 人工标记已处理
ALERT_STATUS_DISMISSED = 2     # 人工忽略（引擎不再覆盖）
ALERT_STATUS_AUTO_RESOLVED = 3  # 条件不再满足，引擎自动消除

ALERT_STATUS_LABELS: dict[int, str] = {
    ALERT_STATUS_ACTIVE: "待处理",
    ALERT_STATUS_RESOLVED: "已处理",
    ALERT_STATUS_DISMISSED: "已忽略",
    ALERT_STATUS_AUTO_RESOLVED: "已自动消除",
}

# 引擎每轮扫描可以改写的状态集合（不含人工终态）
ALERT_ENGINE_WRITABLE_STATUS = (ALERT_STATUS_ACTIVE, ALERT_STATUS_AUTO_RESOLVED)


class TaskAlert(TenantModelBase):
    """任务预警实例"""

    __tablename__ = "biz_task_alert"
    __table_args__ = (
        Index("idx_ta_task_rule", "task_id", "rule_code"),
        Index("idx_ta_stage_level_status", "stage", "level", "status"),
        Index("idx_ta_status_level", "status", "level"),
        {"comment": "任务预警表（调度工作台阶段预警）"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务单 ID（biz_task.id）"
    )
    task_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="任务单号（冗余）"
    )
    stage: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="触发时的任务状态 -1 待分配 0 待派车 1 待装车 2 待发车 3 在途 4 待交车",
    )

    rule_code: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="规则码 ASSIGN_TIMEOUT/DISPATCH_TIMEOUT/LOAD_TIMEOUT/DEPART_TIMEOUT/"
                "ARRIVE_TIMEOUT/DELIVER_TIMEOUT/STAGE_STAGNANT/CAPACITY_ABNORMAL/"
                "LOAD_MISMATCH/NO_ROUTE_PLAN",
    )
    rule_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="命中的覆盖规则 ID（biz_task_alert_rule.id）；空=用内置或租户默认阈值",
    )

    level: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=ALERT_LEVEL_WARN,
        server_default=text("1"), comment="级别 1-关注 2-严重",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=ALERT_STATUS_ACTIVE,
        server_default=text("0"),
        comment="处理状态 0-待处理 1-已处理 2-已忽略 3-已自动消除",
    )

    due_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="应完成时间（时效类才有；滞留/异常类为空）"
    )
    overdue_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="超时分钟数（物化供排序；未超时为 0）",
    )

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="首次触发时间"
    )
    escalated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="升级为「严重」的时间"
    )
    last_scan_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="最近一次扫描命中时间"
    )

    handler_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="认领人 user_id"
    )
    handler_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="认领人姓名（冗余）"
    )
    claimed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="认领时间"
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处理/忽略/自动消除时间"
    )
    resolved_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="处理人 user_id（自动消除为空）"
    )
    resolve_type: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="处置方式 manual/dismiss/auto"
    )
    resolve_remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="处置说明（忽略时必填原因）"
    )

    snapshot_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True,
        comment="触发时上下文快照（客户、线路、台数、基准时间来源），供阈值变更后复盘",
    )
