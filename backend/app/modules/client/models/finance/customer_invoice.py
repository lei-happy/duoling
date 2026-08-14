"""客户发票（销项，租户库）

与进项发票（``biz_vendor_invoice``）**分表分流程**：销项是「我们开给客户」，进项是
「承运商开给我们」，销购方向、状态机、校验与税务用途全不同，共表会得到一张一半字段
永远为空的表（文档 02 §五、11 §2.1）。

三张表分工：

- ``biz_customer_invoice``：票面主表，含购方完整信息与三个金额；
- ``biz_customer_invoice_item``：行明细，**销项一律建行**（票面要打印品名与税率），
  这点与进项票「只有多税率才建行」不同；
- ``biz_customer_invoice_settle_link``：与客户结算单 N:N，支持拆票与合并开票。

状态集 ``{0 草稿, 1 申请中, 3 已开票, 4 已撤销, 9 已作废}``：红冲不是独立状态，而是
「原票置 9 + 自动生成一张金额取负的反向发票」，用 ``red_flush_from_id`` 串起来。
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

CUSTOMER_INVOICE_DOC_KIND = "customer_invoice"


class CustomerInvoice(FinanceDocBaseMixin, TenantModelBase):
    """客户发票主表（销项）"""

    __tablename__ = "biz_customer_invoice"
    __table_args__ = (
        Index("idx_cinv_customer", "customer_id", "issued_at"),
        Index("idx_cinv_status", "status"),
        Index("idx_cinv_entity", "seller_entity_id"),
        Index("uk_cinv_no_dedup", "dedup_key", unique=True),
        {"comment": "客户发票主表（销项发票）"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=CUSTOMER_INVOICE_DOC_KIND,
        server_default=CUSTOMER_INVOICE_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 customer_invoice）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="收/付方向（销项固定 1-收款侧）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 1-申请中 3-已开票 4-已撤销 9-已作废(含红冲)",
    )

    # ===== 客户与开票主体 =====
    customer_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer.id"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称（冗余）"
    )
    seller_entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="销方经营主体ID（biz_business_entity.id），多主体分别申报",
    )
    seller_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="票面销方名称（冻结冗余）"
    )
    seller_tax_no: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="票面销方税号"
    )

    # ===== 购方信息（冗余冻结：客户档案事后改抬头不应影响已开票据） =====
    buyer_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="购方名称（开票抬头）"
    )
    buyer_tax_no: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="购方税号"
    )
    buyer_address: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="购方地址"
    )
    buyer_phone: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="购方电话"
    )
    buyer_bank: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="购方开户行"
    )
    buyer_account: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="购方银行账号"
    )

    # ===== 票面要素 =====
    invoice_type: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="发票类型 1-普票 2-专票 3-电子普票 4-电子专票 5-其他",
    )
    invoice_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发票号码（开票完成时录入）"
    )
    invoice_code: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="发票代码"
    )
    invoice_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="票面开票日期"
    )
    applicant_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="申请开票时间"
    )
    issued_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开票完成时间"
    )

    # ===== 金额（amount_incl_tax = amount_excl_tax + tax_amount，服务层校验） =====
    amount_excl_tax: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", comment="不含税金额合计"
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", comment="税额合计"
    )
    amount_incl_tax: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="含税金额合计（与基类 planned_amount 同值，报表用语义列）",
    )
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="主税率 %（多税率时留空，按行明细）"
    )

    # ===== 关联结算单（冗余计数） =====
    settle_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联结算单数量"
    )

    # ===== 作废与红冲 =====
    void_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="作废/红冲原因"
    )
    voided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="作废时间"
    )
    is_red_flush: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否红冲票（金额为负） 0-否 1-是",
    )
    red_flush_from_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="红冲票指向的原发票ID；原票上反向不存，查红冲票即可",
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="发票 PDF / 影像 URL"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(90), nullable=True,
        comment="唯一键 invoice_code:invoice_no，防同号票重复录；"
                "未开票、作废、软删时置 NULL",
    )

    @staticmethod
    def build_dedup_key(invoice_code: Optional[str], invoice_no: str) -> str:
        return f"{(invoice_code or '').strip()}:{(invoice_no or '').strip()}"


class CustomerInvoiceItem(TenantModelBase):
    """客户发票行明细（票面打印项，销项一律建行）"""

    __tablename__ = "biz_customer_invoice_item"
    __table_args__ = (
        Index("idx_cii_invoice", "invoice_id"),
        {"comment": "客户发票行明细表"},
    )
    __table_tier__ = "business"

    invoice_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_invoice.id"
    )
    item_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="商品/服务名称（如「汽车整车运输服务」）",
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
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="行序"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )


class CustomerInvoiceSettleLink(TenantModelBase):
    """客户发票 ↔ 客户结算单桥接（支持拆票与合并开票）"""

    __tablename__ = "biz_customer_invoice_settle_link"
    __table_args__ = (
        Index("idx_cisl_invoice", "invoice_id"),
        Index("idx_cisl_settle", "settle_id"),
        Index("uk_cisl_dedup", "dedup_key", unique=True),
        {"comment": "客户发票-结算单桥接表"},
    )
    __table_tier__ = "business"

    invoice_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_invoice.id"
    )
    settle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_settlement.id"
    )
    settle_doc_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="结算单号（冗余）"
    )
    applied_amount_incl_tax: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="本发票对该结算单的开票金额（含税，> 0）",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 invoice_id:settle_id，同一对关系一条；解除（软删）时置 NULL",
    )

    @staticmethod
    def build_dedup_key(invoice_id: int, settle_id: int) -> str:
        return f"{int(invoice_id)}:{int(settle_id)}"
