"""客户发票（销项）Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import InvoiceType
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_DOC_KIND = "customer_invoice"


class CustomerInvoiceItemIn(BaseModel):
    """开票行（金额三项任填两项，第三项自动算）"""

    itemName: Optional[str] = Field(
        default=None, max_length=100, description="品名，留空按「运输服务」",
    )
    taxRate: Optional[Decimal] = Field(
        default=None, ge=0, le=100, description="税率百分数，如 9 表示 9%",
    )
    amountExclTax: Optional[Decimal] = None
    taxAmount: Optional[Decimal] = None
    amountInclTax: Optional[Decimal] = None
    sortOrder: Optional[int] = None
    remark: Optional[str] = Field(default=None, max_length=255)


class CustomerInvoiceItemOut(BaseModel):
    id: int
    invoiceId: int
    itemName: Optional[str] = None
    taxRate: Optional[float] = None
    amountExclTax: float = 0
    taxAmount: float = 0
    amountInclTax: float = 0
    sortOrder: int = 0
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "CustomerInvoiceItemOut":
        return cls(
            id=m.id,
            invoiceId=m.invoice_id,
            itemName=m.item_name,
            taxRate=_f(m.tax_rate),
            amountExclTax=_f0(m.amount_excl_tax),
            taxAmount=_f0(m.tax_amount),
            amountInclTax=_f0(m.amount_incl_tax),
            sortOrder=int(m.sort_order or 0),
            remark=m.remark,
        )


class InvoiceSettleLinkOut(BaseModel):
    """发票关联的结算单行"""

    id: int
    invoiceId: int
    settleId: int
    settleDocNo: Optional[str] = None
    appliedAmount: float = 0
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "InvoiceSettleLinkOut":
        return cls(
            id=m.id,
            invoiceId=m.invoice_id,
            settleId=m.settle_id,
            settleDocNo=m.settle_doc_no,
            appliedAmount=_f0(m.applied_amount_incl_tax),
            remark=m.remark,
        )


class InvoiceSettleCandidateOut(BaseModel):
    """可开票的结算单候选"""

    settleId: int
    docNo: str
    plannedAmount: float = 0
    invoicedAmount: float = 0
    availableAmount: float = 0
    appliedAmount: float = 0
    status: int = 0
    dueDate: Optional[date] = None
    receivedAt: Optional[datetime] = None
    invoiceRequired: int = 0


class PendingInvoiceSettleOut(BaseModel):
    """待开票池一行（催开票用）"""

    settleId: int
    docNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    plannedAmount: float = 0
    invoicedAmount: float = 0
    gapAmount: float = 0
    status: int = 0
    dueDate: Optional[date] = None
    receivedAt: Optional[datetime] = None


class CustomerInvoiceListItem(BaseModel):
    """台账列表行"""

    id: int
    docNo: str
    customerId: int
    customerName: Optional[str] = None
    sellerEntityId: Optional[int] = None
    sellerTitle: Optional[str] = None
    buyerTitle: Optional[str] = None
    invoiceType: int = 2
    invoiceTypeLabel: Optional[str] = None
    invoiceNo: Optional[str] = None
    invoiceCode: Optional[str] = None
    invoiceDate: Optional[date] = None
    applicantAt: Optional[datetime] = None
    issuedAt: Optional[datetime] = None
    amountExclTax: float = 0
    taxRate: Optional[float] = None
    taxAmount: float = 0
    amountInclTax: float = 0
    settleCount: int = 0
    isRedFlush: int = 0
    redFlushFromId: Optional[int] = None
    status: int
    statusLabel: Optional[str] = None
    isLocked: int = 0
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "CustomerInvoiceListItem":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            sellerEntityId=m.seller_entity_id,
            sellerTitle=m.seller_title,
            buyerTitle=m.buyer_title,
            invoiceType=int(m.invoice_type or 0),
            invoiceTypeLabel=InvoiceType.LABELS.get(int(m.invoice_type or 0)),
            invoiceNo=m.invoice_no,
            invoiceCode=m.invoice_code,
            invoiceDate=m.invoice_date,
            applicantAt=m.applicant_at,
            issuedAt=m.issued_at,
            amountExclTax=_f0(m.amount_excl_tax),
            taxRate=_f(m.tax_rate),
            taxAmount=_f0(m.tax_amount),
            amountInclTax=_f0(m.amount_incl_tax),
            settleCount=int(m.settle_count or 0),
            isRedFlush=int(m.is_red_flush or 0),
            redFlushFromId=m.red_flush_from_id,
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _DOC_KIND),
            isLocked=int(m.is_locked or 0),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class CustomerInvoiceOut(CustomerInvoiceListItem):
    """详情"""

    sellerTaxNo: Optional[str] = None
    buyerTaxNo: Optional[str] = None
    buyerAddress: Optional[str] = None
    buyerPhone: Optional[str] = None
    buyerBank: Optional[str] = None
    buyerAccount: Optional[str] = None
    pdfUrl: Optional[str] = None
    voidReason: Optional[str] = None
    voidedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    items: List[CustomerInvoiceItemOut] = Field(default_factory=list)
    settles: List[InvoiceSettleLinkOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)
    # 作废跨月等场景的提醒文案，由服务层给出
    warning: Optional[str] = None

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        items: Optional[List[Any]] = None,
        settles: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
        warning: Optional[str] = None,
    ) -> "CustomerInvoiceOut":
        base = CustomerInvoiceListItem.from_model(m).model_dump()
        return cls(
            **base,
            sellerTaxNo=m.seller_tax_no,
            buyerTaxNo=m.buyer_tax_no,
            buyerAddress=m.buyer_address,
            buyerPhone=m.buyer_phone,
            buyerBank=m.buyer_bank,
            buyerAccount=m.buyer_account,
            pdfUrl=m.pdf_url,
            voidReason=m.void_reason,
            voidedAt=m.voided_at,
            cancelReason=m.cancel_reason,
            items=[CustomerInvoiceItemOut.from_model(x) for x in (items or [])],
            settles=[InvoiceSettleLinkOut.from_model(x) for x in (settles or [])],
            actions=actions or {},
            warning=warning,
        )


class InvoiceAllocationIn(BaseModel):
    settleId: int
    appliedAmount: Optional[Decimal] = Field(
        default=None, gt=0, description="留空按该结算单可开票余额全额开",
    )
    remark: Optional[str] = Field(default=None, max_length=255)


class CustomerInvoiceCreateRequest(BaseModel):
    customerId: int
    allocations: List[InvoiceAllocationIn] = Field(min_length=1)
    invoiceType: int = Field(default=InvoiceType.SPECIAL, ge=1, le=5)
    sellerEntityId: Optional[int] = None
    sellerTitle: Optional[str] = Field(default=None, max_length=100)
    sellerTaxNo: Optional[str] = Field(default=None, max_length=30)
    buyerTitle: Optional[str] = Field(default=None, max_length=100)
    buyerTaxNo: Optional[str] = Field(default=None, max_length=30)
    buyerAddress: Optional[str] = Field(default=None, max_length=200)
    buyerPhone: Optional[str] = Field(default=None, max_length=30)
    buyerBank: Optional[str] = Field(default=None, max_length=100)
    buyerAccount: Optional[str] = Field(default=None, max_length=50)
    taxRate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    items: List[CustomerInvoiceItemIn] = Field(
        default_factory=list,
        description="留空按关联金额自动建一行「运输服务」",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class CustomerInvoiceUpdateRequest(BaseModel):
    invoiceType: Optional[int] = Field(default=None, ge=1, le=5)
    sellerEntityId: Optional[int] = None
    sellerTitle: Optional[str] = Field(default=None, max_length=100)
    sellerTaxNo: Optional[str] = Field(default=None, max_length=30)
    buyerTitle: Optional[str] = Field(default=None, max_length=100)
    buyerTaxNo: Optional[str] = Field(default=None, max_length=30)
    buyerAddress: Optional[str] = Field(default=None, max_length=200)
    buyerPhone: Optional[str] = Field(default=None, max_length=30)
    buyerBank: Optional[str] = Field(default=None, max_length=100)
    buyerAccount: Optional[str] = Field(default=None, max_length=50)
    taxRate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    items: Optional[List[CustomerInvoiceItemIn]] = None
    remark: Optional[str] = Field(default=None, max_length=500)


class InvoiceLinkRequest(BaseModel):
    allocations: List[InvoiceAllocationIn] = Field(min_length=1)


class InvoiceItemsRequest(BaseModel):
    items: List[CustomerInvoiceItemIn] = Field(min_length=1)


class InvoiceIssueRequest(BaseModel):
    invoiceNo: str = Field(min_length=1, max_length=50)
    invoiceCode: Optional[str] = Field(default=None, max_length=30)
    invoiceDate: Optional[date] = None
    pdfUrl: Optional[str] = Field(default=None, max_length=500)


class InvoiceReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
