"""能源异常记录（租户库）"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, BigInteger, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyException(TenantModelBase):
    """能源异常记录"""

    __tablename__ = "biz_energy_exception"
    __table_args__ = (
        Index("idx_energy_exc_status", "status"),
        Index("idx_energy_exc_cons", "consumption_id"),
        {"comment": "能源异常记录表"},
    )
    __table_tier__ = "business"

    consumption_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="消费流水 ID"
    )
    account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="能源账户 ID"
    )
    exception_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="异常类型"
    )
    risk_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="MEDIUM", comment="风险等级"
    )
    exception_message: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="异常说明"
    )
    context_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="上下文快照"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending",
        comment="状态 pending/processed/ignored",
    )
    processor_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="处理人 user_id"
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处理时间"
    )
    process_remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="处理备注"
    )
