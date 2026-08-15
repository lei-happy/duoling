"""能源充值单（租户库）

一期自带「登记付款」动作，不进出纳打款批次。
# 二期接入点：PayableDocKind + PaymentBatchService._DOC_MODELS / _pay_source_doc
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin


class EnergyRecharge(FinanceDocBaseMixin, TenantModelBase):
    """能源充值单"""

    __tablename__ = "biz_energy_recharge"
    __table_args__ = (
        Index("idx_energy_recharge_account", "account_id"),
        Index("idx_energy_recharge_status", "status"),
        {"comment": "能源充值单"},
    )
    __table_tier__ = "business"

    account_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="能源账户 ID"
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="供应商 ID（冗余）"
    )
    recharge_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="充值发生时间"
    )
    bank_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="付款银行账户 ID（biz_bank_account，仅记录）"
    )
    bank_account_label: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="付款账户快照"
    )
    payment_reference: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="银行回单号 / 付款凭证号"
    )
    ledger_txn_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="入账流水 ID（biz_energy_account_txn）"
    )
