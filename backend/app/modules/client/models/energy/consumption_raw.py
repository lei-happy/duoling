"""能源消费原始数据（租户库，只增不改）"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, BigInteger, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyConsumptionRaw(TenantModelBase):
    """能源消费原始数据"""

    __tablename__ = "biz_energy_consumption_raw"
    __table_args__ = (
        Index("uk_energy_raw_hash", "data_hash", unique=True),
        Index("idx_energy_raw_supplier", "supplier_id", "process_status"),
        Index("idx_energy_raw_external", "external_transaction_id"),
        {"comment": "能源消费原始数据表（只增不改）"},
    )
    __table_tier__ = "business"

    supplier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="供应商 ID"
    )
    connector_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="连接器实例 ID"
    )
    external_transaction_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="供应商流水号"
    )
    raw_data: Mapped[Any] = mapped_column(
        JSON, nullable=False, comment="原始 JSON"
    )
    data_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="去重指纹"
    )
    process_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending",
        comment="处理状态 pending/processed/duplicate/failed",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="处理失败原因"
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="接收时间"
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处理完成时间"
    )
    consumption_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="生成的标准流水 ID"
    )
