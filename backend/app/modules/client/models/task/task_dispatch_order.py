"""
任务单调令表（租户库）

一个任务单可由 N 条调令组成（A→B 重驶、B→C 空驶、…），每条调令是一段
"完整运输运动"，承担调度/成本归属的最小单元。

调令类型（dispatch_type）：
- 1 重驶：拉着商品车的实际运输段
- 2 空驶：空车回程或调拨段（无 cargo，但需归属到某个任务任务作为成本）
- 3 年检：年检调拨
- 4 应急：应急调拨（事故/抢救）
- 5 其他：其他业务调拨

时间字段语义：
- planned_load_time / planned_arrive_time：调度计划
- accepted_at：司机端确认接收调令（lite 端调令池上报）
- started_at：司机点击"开始执行"（出发前）
- actual_load_time / actual_arrive_time：实际装车 / 实际到达
- completed_at：调令完成（一般等于 actual_arrive_time，预留独立确认入口）

兼容历史：原 ``biz_task_segment`` 重命名为 ``biz_task_dispatch_order``；
原 ``segment_no`` → ``order_no``。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Numeric, SmallInteger, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskDispatchOrder(TenantModelBase):
    """任务单调令（一段完整运输运动 = 一条调令）"""

    __tablename__ = "biz_task_dispatch_order"
    __table_args__ = (
        Index("idx_dispatch_order_task_id", "task_id"),
        Index("idx_dispatch_order_dispatch_type", "dispatch_type"),
        UniqueConstraint("task_id", "order_no", name="uk_task_dispatch_order"),
        {"comment": "任务单调令表（运输任务的最小调度单位）"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    order_no: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="调令序号 1,2,3..."
    )
    dispatch_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="调令类型 1-重驶 2-空驶 3-年检 4-应急 5-其他",
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
        Numeric(8, 2), nullable=True, comment="调令公里数"
    )

    planned_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划装车时间"
    )
    planned_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划到达时间"
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="调令接收时间（司机端确认）"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="调令开始时间（司机点击出发）"
    )
    actual_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际装车时间"
    )
    actual_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际到达时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="调令完成时间"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="调令状态 0-待装车 1-装车中 2-在途 3-已到达 4-已卸车",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
