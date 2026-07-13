"""
智能配载 - 生成任务表（biz_smart_stowage_task）

一次「一键生成配载方案」的请求即一条生成任务。沿用与承运运费计算任务
（biz_carrier_freight_calc_task）一致的认领模式：

- 手动生成（本版）：API 内同步执行，状态 pending -> running -> success；
- 定时自动预配（预留）：worker 认领 status=pending 的任务异步执行。

两条路径不冲突：worker 只 claim `pending`，同步路径直接置为 running。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SmartStowagePlanTask(TenantModelBase):
    """智能配载方案生成任务"""

    __tablename__ = "biz_smart_stowage_task"
    __table_args__ = (
        Index("idx_sst_status_created", "status", "created_at"),
        Index("idx_sst_trigger_user", "triggered_by_user_id"),
        {"comment": "智能配载方案生成任务表"},
    )
    __table_tier__ = "business"

    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="状态 pending/running/success/failed",
    )

    filter_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="候选筛选条件快照(JSON)"
    )
    params_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="算法参数快照(JSON)：targetSpots/权重/占位系数覆盖等"
    )

    candidate_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="参与计算的候选行数",
    )
    plan_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="产出方案数",
    )
    adopted_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="已采纳方案数",
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
    triggered_by_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="触发用户名"
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )
