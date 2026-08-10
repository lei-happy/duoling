"""
任务单状态事件表（租户库）

``biz_task_status_event`` 是任务领域的"事实流水"，用于还原一张任务单的完整时间流：
谁、在什么时候、通过哪个端、把任务从哪个状态推到了哪个状态、为什么。

与既有时间戳字段（``assigned_at`` / ``dispatched_at`` / ``actual_load_time`` …）的关系：
那些字段只保留"最后一次"的结果，撤销重做后会被覆盖；本表保留每一次动作，
撤销与取消也各自成为一条事件，因此时间轴与审计以本表为准。

设计要点：
- **append-only**：不更新、不删除；撤销通过反向事件表达。
- **冗余足够**：任务单号、操作人姓名冗余落库，任务软删除后事件仍可解释。
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON, BigInteger, DateTime, Index, SmallInteger, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


# 事件类型：正向 1~9，逆向 11~16
TASK_EVENT_CREATE = 1
TASK_EVENT_ASSIGN_CARRIER = 2
TASK_EVENT_DISPATCH = 3
TASK_EVENT_LOAD = 4
TASK_EVENT_DEPART = 5
TASK_EVENT_ARRIVE = 6
TASK_EVENT_DELIVER = 7
TASK_EVENT_CLOSE = 8
TASK_EVENT_CANCEL = 9
TASK_EVENT_REVERT_DISPATCH = 11
TASK_EVENT_REVERT_LOAD = 12
TASK_EVENT_REVERT_DEPART = 13
TASK_EVENT_REVERT_ARRIVE = 14
TASK_EVENT_REVERT_DELIVER = 15
TASK_EVENT_FORCE_CANCEL = 16

TASK_EVENT_LABELS: dict[int, str] = {
    TASK_EVENT_CREATE: "创建任务",
    TASK_EVENT_ASSIGN_CARRIER: "分配承运方",
    TASK_EVENT_DISPATCH: "派车",
    TASK_EVENT_LOAD: "装车完成",
    TASK_EVENT_DEPART: "出发",
    TASK_EVENT_ARRIVE: "到达",
    TASK_EVENT_DELIVER: "交车完成",
    TASK_EVENT_CLOSE: "关闭任务",
    TASK_EVENT_CANCEL: "取消任务",
    TASK_EVENT_REVERT_DISPATCH: "撤回派车",
    TASK_EVENT_REVERT_LOAD: "撤销装车",
    TASK_EVENT_REVERT_DEPART: "撤回出发",
    TASK_EVENT_REVERT_ARRIVE: "撤回到达",
    TASK_EVENT_REVERT_DELIVER: "撤销交车",
    TASK_EVENT_FORCE_CANCEL: "强制取消",
}


# 事件来源
TASK_EVENT_SOURCE_CLIENT = 1      # 企业端（调度员操作）
TASK_EVENT_SOURCE_DRIVER = 2      # 驾驶员 H5 / 小程序
TASK_EVENT_SOURCE_CARRIER = 3     # 承运商 LITE
TASK_EVENT_SOURCE_SYSTEM = 4      # 系统聚合（item 聚合驱动的状态跳转）
TASK_EVENT_SOURCE_BACKFILL = 5    # 历史回填

TASK_EVENT_SOURCE_LABELS: dict[int, str] = {
    TASK_EVENT_SOURCE_CLIENT: "企业端",
    TASK_EVENT_SOURCE_DRIVER: "驾驶员端",
    TASK_EVENT_SOURCE_CARRIER: "承运商端",
    TASK_EVENT_SOURCE_SYSTEM: "系统聚合",
    TASK_EVENT_SOURCE_BACKFILL: "历史回填",
}


class TaskStatusEvent(TenantModelBase):
    """任务单状态事件（append-only 事实流）"""

    __tablename__ = "biz_task_status_event"
    __table_args__ = (
        Index("idx_tse_task_time", "task_id", "event_time"),
        Index("idx_tse_task_to_status", "task_id", "to_status"),
        {"comment": "任务单状态事件表（时间流 / 审计）"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务单 ID"
    )
    task_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="任务单号（冗余）"
    )
    event_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="事件类型 1-创建 2-分配承运 3-派车 4-装车 5-出发 6-到达 7-交车 "
                "8-关闭 9-取消 11-撤回派车 12-撤销装车 13-撤回出发 14-撤回到达 "
                "15-撤销交车 16-强制取消",
    )
    from_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="变更前状态"
    )
    to_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="变更后状态"
    )
    source: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="来源 1-企业端 2-驾驶员端 3-承运商端 4-系统聚合 5-历史回填",
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="原因 / 备注"
    )
    payload_snapshot: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="关键字段快照（车牌、司机、台数等）"
    )
    event_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="事件时间"
    )
