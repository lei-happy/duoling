"""能源同步任务队列（租户库）"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergySyncTask(TenantModelBase):
    """能源同步任务"""

    __tablename__ = "biz_energy_sync_task"
    __table_args__ = (
        Index("idx_energy_sync_status", "status", "priority", "created_at"),
        Index("idx_energy_sync_connector", "connector_id"),
        {"comment": "能源同步任务队列"},
    )
    __table_tier__ = "business"

    task_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="任务类型 pull/import/normalize/allocate/snapshot"
    )
    connector_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="连接器 ID"
    )
    target_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="目标类型"
    )
    target_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="目标 ID"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending",
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
        String(1000), nullable=True, comment="最近一次错误"
    )
    payload_json: Mapped[Optional[str]] = mapped_column(
        String(2000), nullable=True, comment="任务参数 JSON"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )
