"""能源账户（租户库）

账面余额只能由 biz_energy_account_txn 改变。
available_balance / diff_amount 用属性派生，不落库。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Numeric, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyAccount(TenantModelBase):
    """能源账户"""

    __tablename__ = "biz_energy_account"
    __table_args__ = (
        Index("uk_energy_account_code", "account_code", unique=True),
        Index("idx_energy_account_supplier", "supplier_id"),
        {"comment": "能源账户表"},
    )
    __table_tier__ = "business"

    account_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="账户编码（租户内唯一）"
    )
    account_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="账户名称"
    )
    supplier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="供应商 ID"
    )
    energy_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="能源类型 OIL/GAS/ELECTRIC/OTHER"
    )
    account_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="PREPAID", server_default=text("'PREPAID'"),
        comment="账户类型 PREPAID/POSTPAID/CREDIT/CARD_POOL/VIRTUAL",
    )
    external_account_no: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="供应商侧账号"
    )
    currency: Mapped[str] = mapped_column(
        String(8), nullable=False, default="CNY", server_default=text("'CNY'"),
        comment="币种",
    )
    ledger_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="账面余额（唯一事实来源：Σ txn.delta）",
    )
    supplier_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="供应商侧余额（对账用）"
    )
    frozen_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="冻结金额",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常 2-冻结 3-已关闭",
    )
    last_sync_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近同步时间"
    )
    last_txn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近一笔流水时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )

    @property
    def available_balance(self) -> Decimal:
        return (self.ledger_balance or Decimal("0")) - (self.frozen_amount or Decimal("0"))

    @property
    def diff_amount(self) -> Optional[Decimal]:
        if self.supplier_balance is None:
            return None
        return (self.ledger_balance or Decimal("0")) - self.supplier_balance
