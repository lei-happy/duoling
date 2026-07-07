"""
资金流水（租户库，append-only，收款方泛化）

资金账户 ``biz_driver_fund_account.balance`` 的唯一事实来源：
``balance == Σ delta``。流水只增不改不删，写错只能新增反向冲正流水。
按 ``(owner_type, owner_id)`` 标识收款方（自有司机/社会运力/承运商）。
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, Index, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverFundTransaction(TenantModelBase):
    """资金流水（收款方泛化）"""

    __tablename__ = "biz_driver_fund_transaction"
    __table_args__ = (
        Index("idx_dft_account", "account_id"),
        Index("idx_dft_owner", "owner_type", "owner_id"),
        Index("idx_dft_biz_type", "biz_type"),
        Index("idx_dft_created", "created_at"),
        {"comment": "资金流水（收款方泛化）"},
    )
    __table_tier__ = "business"

    account_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_driver_fund_account.id"
    )
    owner_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1",
        comment="收款方类型 1-自有司机 2-承运商(预留) 3-社会运力（冗余）",
    )
    owner_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False,
        comment="收款方ID（冗余，便于按收款方查）",
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="冗余经营主体ID"
    )
    txn_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="流水号（系统生成）"
    )
    biz_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment=(
            "业务类型 1-预付登记 2-退款入账 3-人工入账 4-人工出账 5-人工调整 "
            "6-任务抵扣(二期) 7-任务结算入账(二期)"
        ),
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="方向 1-入 2-出（由 delta 符号派生，冗余展示）",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="金额（正数，展示用）"
    )
    delta: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="带符号变动额（记账用，=±amount）"
    )
    balance_before: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="记账前余额快照"
    )
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="记账后余额快照"
    )
    related_task_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联 biz_task.id（可空）"
    )
    related_finance_doc_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联 biz_task_finance_doc.id（可空）"
    )
    source: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", nullable=False,
        comment="来源 1-手工 2-系统联动（二期）",
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="凭证图片 URL"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
