"""
任务单运输分段表（租户库）

一个任务单可有 N 段运输（A→B→C→D），每段独立的装卸/到达时间与状态。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Numeric, SmallInteger, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskSegment(TenantModelBase):
    """任务单运输分段"""

    __tablename__ = "biz_task_segment"
    __table_args__ = (
        Index("idx_segment_task_id", "task_id"),
        UniqueConstraint("task_id", "segment_no", name="uk_task_segment"),
        {"comment": "任务单运输分段表"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    segment_no: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="段序号 1,2,3..."
    )
    from_location: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="起点名称"
    )
    from_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="起点编码"
    )
    from_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="起点行政区 ID"
    )
    to_location: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="终点名称"
    )
    to_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="终点编码"
    )
    to_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="终点行政区 ID"
    )
    mileage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2), nullable=True, comment="段公里数"
    )
    planned_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划装车时间"
    )
    planned_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划到达时间"
    )
    actual_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际装车时间"
    )
    actual_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际到达时间"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="段状态 0-待装车 1-装车中 2-在途 3-已到达 4-已卸车",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
