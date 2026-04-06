"""
待办任务（平台库）

业务数据归属租户，creator_id / assignee_id 均为该 tenant_code 对应租户库中 biz_user.id。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysTodoTask(PlatformModelBase):
    """待办任务表"""

    __tablename__ = "sys_todo_task"
    __table_args__ = (
        Index("idx_sys_todo_tenant_assignee_status", "tenant_code", "assignee_id", "status"),
        Index("idx_sys_todo_tenant_status", "tenant_code", "status"),
        Index("idx_sys_todo_due_time", "due_time"),
        {"comment": "待办任务（平台库；人员 ID 为租户内 biz_user.id，须与 tenant_code 联用）"},
    )

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True, comment="租户编码"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="描述")
    creator_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="创建人，租户内 biz_user.id（与 tenant_code 联用）",
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="主责任人，租户内 biz_user.id（与 tenant_code 联用）",
    )
    creator_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="创建人姓名快照"
    )
    assignee_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="责任人姓名快照"
    )
    due_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="截止时间")
    priority: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="优先级 0低/1中/2高"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0待处理/1进行中/2已完成/3已关闭",
    )
    completed_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )
