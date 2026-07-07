"""
成本计算任务表（异步重算工作流，与收入侧 biz_freight_calc_task 对称）
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CostCalcTask(TenantModelBase):
    """成本计算任务（worker 扫表执行）

    task_type:
      - task_dispatched   : 任务派车/发运触发
      - task_changed      : 任务计费敏感字段变更
      - policy_changed    : 成本政策变更
      - rule_changed      : 单条成本规则变更
      - manual_recalc     : 手动重算（前端按钮）
    target_type / target_id : 任务的直接目标，例如 ('task', 123)
    """

    __tablename__ = "biz_cost_calc_task"
    __table_args__ = (
        Index("idx_cct_status_priority", "status", "priority", "created_at"),
        Index("idx_cct_target", "target_type", "target_id"),
        Index("idx_cct_task", "task_id"),
        {"comment": "成本计算任务表"},
    )
    __table_tier__ = "business"

    task_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="任务类型"
    )
    target_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="目标类型 task/policy/rule"
    )
    target_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="目标ID"
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="冗余的任务ID（政策/规则触发时由展开阶段写入；task_changed 与 target_id 相同）",
    )

    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="状态 pending/running/success/failed",
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="优先级（越大越优先）",
    )

    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="已重试次数",
    )
    max_retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default=text("3"),
        comment="最大重试次数",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="最近一次错误信息"
    )

    triggered_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="触发用户ID"
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )
