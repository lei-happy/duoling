"""承运商结算单（租户库）

基于一张或多张「已确认」承运商对账单进入审批与付款流程（文档 03 §四）。表名带
``_doc`` 后缀是为了避开 ``biz_carrier_settlement``——那是承运商的**结算账户**档案，
两者语义完全不同，重名会让人在 SQL 里查错表。

金额三列的分工与客户结算单对称：

- ``planned_amount``：计划付款额，= Σ 桥接行 ``applied_amount``；
- ``paid_amount_total``：已付累计（打款批次分批执行时递增）；
- ``actual_amount``：正式付妥金额，满额置 ``status=3`` 时一次写入。

``is_offset_only=1`` 是纯抵账场景：任务级预付已把钱付完，对账净额为 0，这张单只做
账面闭环，不需要付款凭证。

进项票两列（``invoice_matched`` / ``invoice_amount_total``）按文档 11 §三 的要求在
建表时就带上，避免第 3 期内再 ALTER 一次。
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

CARRIER_SETTLE_DOC_KIND = "carrier_settle"


class CarrierSettlementDoc(FinanceDocBaseMixin, TenantModelBase):
    """承运商结算单主表"""

    __tablename__ = "biz_carrier_settlement_doc"
    __table_args__ = (
        Index("idx_castl_carrier_status", "carrier_id", "status"),
        Index("idx_castl_status", "status"),
        Index("idx_castl_enterprise", "enterprise_id"),
        Index("idx_castl_due_date", "due_date"),
        Index("idx_castl_invoice", "invoice_matched", "status"),
        {"comment": "承运商结算单主表（区别于 biz_carrier_settlement 结算账户）"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=CARRIER_SETTLE_DOC_KIND,
        server_default=CARRIER_SETTLE_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 carrier_settle）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="收/付方向（应付固定 2-付款）",
    )

    # ===== 承运商与归属 =====
    carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier.id"
    )
    carrier_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="承运商名称（冗余）"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="成本归属经营主体ID"
    )

    # ===== 付款账户（付款时校验账户 status=1） =====
    settlement_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="承运商结算账户（biz_carrier_settlement.id）"
    )
    settlement_account_label: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="账户标签（冗余）"
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户行（冗余）"
    )
    bank_account_masked: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="收款账号脱敏（冗余，仅展示后四位）"
    )

    # ===== 关联对账单 =====
    recon_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联对账单数量（冗余）"
    )

    # ===== 付款 =====
    paid_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已付累计（打款批次分批执行时递增）",
    )
    is_offset_only: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否仅抵账（无实付，预付已覆盖全额）0-否 1-是",
    )
    due_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="应付到期日（按承运商结算方式与账期推导）"
    )

    # ===== 进项票核销（文档 11 §三） =====
    invoice_matched: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否已收齐进项票 0-未齐 1-已齐",
    )
    invoice_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已核销进项票含税金额累计",
    )

    # ===== 打款批次（第 4 期落地，本期只留冗余标记） =====
    batch_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="所属打款批次ID（biz_payment_batch.id，第 4 期建表）",
    )
    batch_locked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="入批时间（入批后不允许改金额）"
    )


class CarrierSettleReconLink(TenantModelBase):
    """结算单 ↔ 对账单桥接（带应用金额，支持拆并）"""

    __tablename__ = "biz_carrier_settle_recon_link"
    __table_args__ = (
        Index("idx_casrl_settle", "settle_id"),
        Index("idx_casrl_recon", "recon_id"),
        Index("uk_casrl_dedup", "dedup_key", unique=True),
        {"comment": "承运商结算单-对账单桥接表"},
    )
    __table_tier__ = "business"

    settle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier_settlement_doc.id"
    )
    recon_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier_recon.id"
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
