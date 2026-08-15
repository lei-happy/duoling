"""能源对账单（租户库）"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, SmallInteger, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin


class EnergyRecon(FinanceDocBaseMixin, TenantModelBase):
    """能源对账单"""

    __tablename__ = "biz_energy_recon"
    __table_args__ = (
        Index("idx_energy_recon_account", "account_id"),
        Index("idx_energy_recon_status", "status"),
        {"comment": "能源对账单"},
    )
    __table_tier__ = "business"

    account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="能源账户 ID"
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="供应商 ID"
    )
    recon_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=2, server_default=text("2"),
        comment="对账类型 1-账户余额 2-消费流水",
    )
    external_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="外部账单金额合计",
    )
    internal_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="系统流水金额合计",
    )
    difference_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="差异金额",
    )
    matched_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="已匹配笔数",
    )
    diff_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="差异笔数",
    )
