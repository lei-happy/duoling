"""
派车选择留痕（租户库）

每一次确认派车 / 换车可落一行，记录当时曝光的运力、第一推荐、实际选择。
供采纳率统计与远期智能推荐训练；不记点击流。
"""

from typing import Any, Optional

from sqlalchemy import JSON, BigInteger, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskDispatchSelection(TenantModelBase):
    """派车选择留痕（append-only）"""

    __tablename__ = "biz_task_dispatch_selection"
    __table_args__ = (
        Index("idx_tds_task_id", "task_id"),
        {"comment": "派车选择留痕（推荐曝光与采纳）"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务单 ID"
    )
    dispatcher_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="调度员 user_id"
    )
    dispatcher_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="调度员姓名（冗余）"
    )
    carrier_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="承运方式 1-自有车 2-承运商 3-社会运力"
    )
    engine: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="推荐引擎标识，如 heuristic_v1"
    )
    source: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="选择来源 recommended / search / manual",
    )
    shown_capacity_ids: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="确认时列表曝光的运力 ID"
    )
    top_recommended_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="首次加载（过滤前）第一推荐运力 ID"
    )
    selected_capacity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="实际选中的运力 ID"
    )
    selected_rank: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="点选时的名次（从 1 起）"
    )
    adopted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否采纳第一推荐 1-是 0-否",
    )
