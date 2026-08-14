"""
收款单与核销桥接（租户库）

``biz_receipt_voucher`` 记的是**银行到账这个事实**，不是应收义务——应收义务在
客户结算单。一笔到账可核销到多张结算单，一张结算单也可由多笔到账付清，多对多
关系落在 ``biz_receipt_settle_link``（文档 10 §四）。

状态集 ``{0 草稿, 3 已认领, 5 已核销, 4 已撤销}``：**没有待审批与已审批**——钱到
账是客观事实，不需要审批，这也是它与结算单的本质区别。

金额语义：``planned_amount`` = 到账总额（收款单里到账即实收，``actual_amount``
同值写入以复用基座字段）；``settled_amount`` / ``unsettled_amount`` 是核销进度冗余，
供出纳台筛「还有多少钱没认领」。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin

RECEIPT_VOUCHER_DOC_KIND = "receipt_voucher"


class ReceiptVoucher(FinanceDocBaseMixin, TenantModelBase):
    """收款单（银行到账事实）"""

    __tablename__ = "biz_receipt_voucher"
    __table_args__ = (
        Index("idx_rcpt_customer", "customer_id", "received_at"),
        # 出纳台「待认领到账」按未核销余额筛，故联合索引带 unsettled_amount
        Index("idx_rcpt_unsettled", "status", "unsettled_amount"),
        Index("idx_rcpt_serial", "bank_serial_no"),
        {"comment": "收款单（到账事实）"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=RECEIPT_VOUCHER_DOC_KIND,
        server_default=RECEIPT_VOUCHER_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 receipt_voucher）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="收/付方向（收款固定 1）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿(未核销) 3-已认领(部分核销) 5-已核销(满额) 4-已撤销",
    )

    # ===== 付款方 =====
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="付款客户ID（可空：认领前可能还不确定是谁打的）",
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称（冗余）"
    )
    payer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="银行回单上的付款方名称（原文，可能与客户档案名不同）",
    )

    # ===== 收款账户与到账 =====
    bank_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="收款账户ID（biz_bank_account.id，该表第 4 期建，本期可空）",
    )
    bank_account_label: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="收款账户标签（冗余展示）"
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="到账时间（与基类 paid_at 同值，冗余便于按到账日筛选）",
    )
    receive_method: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="收款方式 1-银行转账 2-现金 3-支票 4-承兑汇票 5-平台代收",
    )
    bank_serial_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="银行流水号（远期自动匹配的关键）"
    )
    voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="银行回单附件 URL"
    )

    # ===== 核销进度（冗余，= Σ 核销明细） =====
    settled_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", comment="已核销金额"
    )
    unsettled_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="未核销金额 = planned_amount - settled_amount",
    )


class ReceiptSettleLink(TenantModelBase):
    """收款单 ↔ 客户结算单 核销桥接"""

    __tablename__ = "biz_receipt_settle_link"
    __table_args__ = (
        Index("idx_rsl_receipt", "receipt_id"),
        Index("idx_rsl_settle", "settle_id"),
        Index("uk_rsl_dedup", "dedup_key", unique=True),
        {"comment": "收款单-客户结算单核销桥接表"},
    )
    __table_tier__ = "business"

    receipt_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_receipt_voucher.id"
    )
    settle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_settlement.id"
    )
    settle_doc_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="结算单号（冗余）"
    )
    applied_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="本收款单核销到该结算单的金额（> 0）",
    )
    settled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="核销时间"
    )
    settled_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="核销操作人 user_id"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 receipt_id:settle_id，同一对关系只一条（追加金额走更新）；"
                "撤销核销（软删）时置 NULL",
    )

    @staticmethod
    def build_dedup_key(receipt_id: int, settle_id: int) -> str:
        return f"{int(receipt_id)}:{int(settle_id)}"
