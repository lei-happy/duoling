"""
官网企业自助注册异步任务（平台库）
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class OpenRegisterTask(PlatformBase):
    """企业注册异步任务进度"""

    __tablename__ = "open_register_task"
    __table_args__ = {"comment": "官网企业注册异步任务"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, comment="任务 UUID")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="pending running success failed",
    )
    current_step: Mapped[str] = mapped_column(
        String(64), default="", comment="当前步骤机器可读 key"
    )
    message: Mapped[str] = mapped_column(
        String(255), default="", comment="当前步骤中文说明"
    )
    percent: Mapped[int] = mapped_column(SmallInteger, default=0, comment="进度 0-100")
    contact_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, comment="用于并发注册防抖查询"
    )
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, comment="RegisterPayload JSON")
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="成功时 RegisterResponse JSON")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="失败原因")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否删除 0-否 1-是"
    )
