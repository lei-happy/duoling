"""
平台库：汽车之家同步任务表 autohome_sync_job
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class AutohomeSyncJob(PlatformBase):
    __tablename__ = "autohome_sync_job"
    __table_args__ = {"comment": "汽车之家数据同步任务", "extend_existing": True}

    job_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="任务ID"
    )
    job_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="probe", comment="任务类型"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="pending", comment="状态"
    )
    progress_pct: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", comment="进度0-100"
    )
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    log_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
