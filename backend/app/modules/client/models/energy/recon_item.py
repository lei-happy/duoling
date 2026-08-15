"""能源对账明细（租户库）"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyReconItem(TenantModelBase):
    """能源对账明细"""

    __tablename__ = "biz_energy_recon_item"
    __table_args__ = (
        Index("idx_energy_recon_item_batch", "recon_id"),
        Index("idx_energy_recon_item_cons", "consumption_id"),
        {"comment": "能源对账明细"},
    )
    __table_tier__ = "business"

    recon_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="对账单 ID"
    )
    consumption_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="系统消费流水 ID"
    )
    external_transaction_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="外部流水号"
    )
    external_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="外部金额"
    )
    internal_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="系统金额"
    )
    difference_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="差异金额"
    )
    recon_result: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="MATCHED/MISSING_INTERNAL/MISSING_EXTERNAL/AMOUNT_DIFF/QTY_DIFF/DUPLICATED",
    )
    process_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending",
        comment="处理状态 pending/confirmed/adjusted/ignored",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
