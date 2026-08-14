"""进项发票（承运商开给我方的票，租户库）

与销项发票不共表：方向相反导致销方/购方、状态机、核销对象、税务用途全线不同，
共表会得到一张一半字段永远为空的表（文档 11 §1.2）。

三张表分工：

- ``biz_vendor_invoice``：票面主表，含销购双方、票号、三个金额与抵扣信息；
- ``biz_vendor_invoice_item``：**仅多税率发票**才建行，单税率直接用主表字段；
- ``biz_vendor_invoice_settle_link``：与承运商结算单 N:N 核销。

状态集 ``{0,3,4,5,9}``：收到票是客观事实，不需要审批，故没有 1/2；``9 已作废``
用于承运商红冲重开，作废时核销明细全部回退。

去重键 ``dedup_key`` 承载「同一张票不重复登记」：值为 ``invoice_code:invoice_no``，
撤销 / 作废 / 软删时置 NULL，让同号票能重新登记（票面录错是常事）。
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Date, DateTime, Index, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin

VENDOR_INVOICE_DOC_KIND = "vendor_invoice"


class VendorInvoice(FinanceDocBaseMixin, TenantModelBase):
    """进项发票主表"""

    __tablename__ = "biz_vendor_invoice"
    __table_args__ = (
        Index("idx_vinv_vendor", "vendor_id", "invoice_date"),
        Index("idx_vinv_status", "status", "unsettled_amount"),
        Index("idx_vinv_deduct", "deduct_period"),
        Index("idx_vinv_entity", "buyer_entity_id"),
        Index("uk_vinv_no_dedup", "dedup_key", unique=True),
        {"comment": "进项发票主表（承运商及其他供应商开给我方的票）"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=VENDOR_INVOICE_DOC_KIND,
        server_default=VENDOR_INVOICE_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 vendor_invoice）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="收/付方向（进项固定 2-付款侧）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 3-已收票（部分核销） 4-已撤销 5-已核销 9-已作废",
    )

    # ===== 销方（供应商） =====
    vendor_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="供应商类型 1-承运商 2-社会运力 3-其他供应商",
    )
    vendor_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="供应商ID（vendor_type=1 时指 biz_carrier.id；其他供应商可空）",
    )
    vendor_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="供应商名称（冗余）"
    )
    seller_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="票面销方名称（原文，可能与档案名不同）"
    )
    seller_tax_no: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="票面销方税号"
    )

    # ===== 购方（我方经营主体） =====
    buyer_entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="购方经营主体ID（biz_business_entity.id），多主体分别申报",
    )
    buyer_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="票面购方名称（冻结冗余）"
    )
    buyer_tax_no: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="票面购方税号"
    )

    # ===== 票面要素 =====
    invoice_type: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="发票类型 1-普票 2-专票 3-电子普票 4-电子专票 5-其他",
    )
    invoice_no: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="发票号码"
    )
    invoice_code: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="发票代码（电子票可空）"
    )
    invoice_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="开票日期（票面日期，非登记日期）"
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="收到票时间（登记时间语义）"
    )

    # ===== 金额（amount_incl_tax = amount_excl_tax + tax_amount，服务层校验） =====
    amount_excl_tax: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", comment="不含税金额"
    )
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="税率 %（多税率时留空，按行明细）"
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", comment="税额"
    )
    amount_incl_tax: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="含税金额（与基类 planned_amount 同值，报表用语义列）",
    )
    is_multi_rate: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否多税率 0-否（用主表金额） 1-是（金额取行明细汇总）",
    )

    # ===== 核销进度（冗余，便于筛「待核销票」） =====
    settled_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已核销金额（= Σ 核销明细 applied_amount）",
    )
    unsettled_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="未核销金额（= 含税金额 - 已核销）",
    )
    settle_count: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="核销的结算单数量"
    )

    # ===== 抵扣与验真 =====
    deductible: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="是否可抵扣 0-否（普票通常） 1-是（专票）",
    )
    deduct_period: Mapped[Optional[str]] = mapped_column(
        String(7), nullable=True, comment="抵扣税期 YYYY-MM（认证抵扣月份）"
    )
    verify_status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="验真状态 0-未验 1-已验通过 2-验真不符（远期对接查验平台）",
    )

    # ===== 作废与附件 =====
    void_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="作废/退票原因"
    )
    voided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="作废时间"
    )
    attachment_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="发票扫描件/PDF URL"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(90), nullable=True,
        comment="唯一键 invoice_code:invoice_no，防重复登记；"
                "撤销/作废/软删置 NULL，允许同号重录",
    )

    @staticmethod
    def build_dedup_key(
        invoice_code: Optional[str], invoice_no: str,
    ) -> str:
        return f"{(invoice_code or '').strip()}:{(invoice_no or '').strip()}"


class VendorInvoiceItem(TenantModelBase):
    """进项发票行明细（仅多税率票使用）"""

    __tablename__ = "biz_vendor_invoice_item"
    __table_args__ = (
        Index("idx_vii_invoice", "invoice_id"),
        {"comment": "进项发票行明细表（多税率场景）"},
    )
    __table_tier__ = "business"

    invoice_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_vendor_invoice.id"
    )
    item_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="品名（如「运输服务」）"
    )
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="税率 %"
    )
    amount_excl_tax: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="不含税金额"
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="税额"
    )
    amount_incl_tax: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="含税金额"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )


class VendorInvoiceSettleLink(TenantModelBase):
    """进项票 ↔ 承运商结算单核销桥接（N:N）"""

    __tablename__ = "biz_vendor_invoice_settle_link"
    __table_args__ = (
        Index("idx_visl_invoice", "invoice_id"),
        Index("idx_visl_settle", "settle_id"),
        Index("uk_visl_dedup", "dedup_key", unique=True),
        {"comment": "进项发票-承运商结算单核销桥接表"},
    )
    __table_tier__ = "business"

    invoice_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_vendor_invoice.id"
    )
    settle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False,
        comment="关联 biz_carrier_settlement_doc.id",
    )
    settle_doc_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="结算单号（冗余）"
    )
    applied_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="本票核销到该结算单的含税金额（> 0）",
    )
    matched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="核销时间"
    )
    matched_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="核销操作人 user_id"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 invoice_id:settle_id，同一对关系一条；撤销核销时置 NULL",
    )

    @staticmethod
    def build_dedup_key(invoice_id: int, settle_id: int) -> str:
        return f"{int(invoice_id)}:{int(settle_id)}"
