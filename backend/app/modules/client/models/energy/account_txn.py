"""能源账户资金流水（租户库，append-only）

ledger_balance == Σ delta。流水只增不改不删，写错只能新增反向冲正流水。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Numeric, SmallInteger, String, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyAccountTxn(TenantModelBase):
    """能源账户资金流水"""

    __tablename__ = "biz_energy_account_txn"
    __table_args__ = (
        Index("uk_energy_txn_no", "txn_no", unique=True),
        Index("idx_energy_txn_account", "account_id", "created_at"),
        Index("idx_energy_txn_external", "external_txn_id"),
        Index("idx_energy_txn_biz", "biz_type", "biz_id"),
        {"comment": "能源账户资金流水表（append-only）"},
    )
    __table_tier__ = "business"

    account_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="能源账户 ID"
    )
    txn_no: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="流水号（系统生成，租户内唯一）"
    )
    txn_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="流水类型 1充值 2消费 3退款 4转入 5转出 6调账 7冲正 8冻结 9解冻 10手续费",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, comment="金额（正数，展示用）"
    )
    delta: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, comment="账面余额带符号变动额"
    )
    frozen_delta: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="冻结金额带符号变动额",
    )
    balance_before: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, comment="记账前账面余额"
    )
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, comment="记账后账面余额"
    )
    external_txn_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="外部流水号"
    )
    biz_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="来源业务类型 recharge/consumption/manual"
    )
    biz_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="来源业务 ID"
    )
    reversed_txn_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="被冲正的原流水 ID"
    )
    transaction_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="业务发生时间"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="备注"
    )
