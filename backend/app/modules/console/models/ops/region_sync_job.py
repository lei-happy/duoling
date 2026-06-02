"""
平台库：行政区域高德同步任务表 region_sync_job
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class RegionSyncJob(PlatformBase):
    __tablename__ = "region_sync_job"
    __table_args__ = {"comment": "行政区域高德同步任务", "extend_existing": True}

    job_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="任务ID"
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
    total_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
