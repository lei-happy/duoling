"""
客户结算单（租户库）

基于一张或多张「已确认」客户对账单，进入审批与收款流程；对账单是事项确认，
结算单才是「确认了要收多少钱」的单据，也是应收账龄的原子单位（文档 02 §4、12 §2.1）。

金额三列的分工（容易混，这里钉死）：

- ``planned_amount``：应收金额，= Σ 桥接行 ``applied_amount``，审批后不再变；
- ``received_amount_total``：已收累计，每次收款核销递增，未满额时单据仍停在
  ``status=2``，账龄按 ``planned_amount - received_amount_total`` 算未收余额；
- ``actual_amount``：**正式收妥金额**，只在满额置 ``status=3`` 时一次写入。

拆并规则见 §4.1：1 张对账单可拆 N 张结算单，N 张对账单可并 1 张结算单，故
``biz_customer_settle_recon_link`` 上带 ``applied_amount`` 表达「本单认领了该对账单
多少钱」。
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Date, DateTime, Index, Integer, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin

CUSTOMER_SETTLE_DOC_KIND = "customer_settle"


class CustomerSettlement(FinanceDocBaseMixin, TenantModelBase):
    """客户结算单主表"""

    __tablename__ = "biz_customer_settlement"
    __table_args__ = (
        # 账龄按 (customer_id, status) 分组聚合，见文档 12 §5.2 的性能兜底
        Index("idx_cstl_customer_status", "customer_id", "status"),
        Index("idx_cstl_status", "status"),
        Index("idx_cstl_enterprise", "enterprise_id"),
        Index("idx_cstl_due_date", "due_date"),
        {"comment": "客户结算单主表"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=CUSTOMER_SETTLE_DOC_KIND,
        server_default=CUSTOMER_SETTLE_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 customer_settle）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="收/付方向（应收固定 1-收款）",
    )

    # ===== 客户与归属 =====
    customer_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer.id"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称（冗余）"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="收入归属经营主体ID（biz_business_entity.id），多主体账龄按此分列",
    )

    # ===== 关联对账单 =====
    recon_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联对账单数量（冗余）"
    )

    # ===== 收款 =====
    received_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已收累计（每次收款核销递增；账龄的已收口径取本列）",
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="收妥时间（与基类 paid_at 同值，应收语义冗余便于筛选）",
    )
    received_voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="银行回单 URL"
    )
    received_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="收款账户ID（biz_bank_account.id，该表第 4 期建，本期可空）",
    )
    received_account_label: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="收款账户标签（冗余展示，免列表 join）"
    )

    # ===== 账期 =====
    due_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True,
        comment="到期日（单据级账期覆盖）。为空时按客户 settlement_type + "
                "payment_days 推导，见文档 12 §2.2",
    )

    # ===== 开票（发票表第 4 期建，本期只维护冗余计数） =====
    invoice_required: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否需要开票 0-否 1-是"
    )
    invoice_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="已关联发票数量（冗余）"
    )
    invoice_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已开发票金额合计（冗余）",
    )


class CustomerSettleReconLink(TenantModelBase):
    """结算单 ↔ 对账单桥接（带应用金额，支持拆并与部分结清）"""

    __tablename__ = "biz_customer_settle_recon_link"
    __table_args__ = (
        Index("idx_csrl_settle", "settle_id"),
        Index("idx_csrl_recon", "recon_id"),
        Index("uk_csrl_dedup", "dedup_key", unique=True),
        {"comment": "客户结算单-对账单桥接表"},
    )
    __table_tier__ = "business"

    settle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_settlement.id"
    )
    recon_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_recon.id"
    )
    recon_doc_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="对账单号（冗余）"
    )
    applied_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="本结算单认领该对账单的金额（Σ 本列 = 结算单 planned_amount）",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 settle_id:recon_id，防重复关联；解除关联（软删）时置 NULL",
    )

    @staticmethod
    def build_dedup_key(settle_id: int, recon_id: int) -> str:
        return f"{int(settle_id)}:{int(recon_id)}"
