"""能源账户每日余额快照（租户库）"""

from decimal import Decimal
from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Date, Index, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyAccountDailySnapshot(TenantModelBase):
    """能源账户每日余额快照"""

    __tablename__ = "biz_energy_account_daily_snapshot"
    __table_args__ = (
        Index("uk_energy_acct_snapshot", "account_id", "snapshot_date", unique=True),
        Index("idx_energy_acct_snapshot_date", "snapshot_date"),
        {"comment": "能源账户每日余额快照"},
    )
    __table_tier__ = "business"

    account_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="能源账户 ID"
    )
    snapshot_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="快照日期"
    )
    opening_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="期初账面余额",
    )
    recharge_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="当日充值",
    )
    consumption_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="当日消费",
    )
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="当日退款",
    )
    adjustment_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="当日调账（带符号）",
    )
    closing_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="期末账面余额",
    )
    supplier_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="当日供应商侧余额"
    )
    frozen_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="期末冻结金额",
    )
