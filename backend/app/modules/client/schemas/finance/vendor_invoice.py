"""进项发票 Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import (
    InvoiceType,
    VendorType,
    VerifyStatus,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_DOC_KIND = "vendor_invoice"


class VendorInvoiceItemIn(BaseModel):
    """多税率发票行（税率必填，金额三项任填两项）"""

    itemName: Optional[str] = Field(default=None, max_length=100)
    taxRate: Decimal = Field(ge=0, le=100, description="税率百分数，如 9 表示 9%")
    amountExclTax: Optional[Decimal] = None
    taxAmount: Optional[Decimal] = None
    amountInclTax: Optional[Decimal] = None
    remark: Optional[str] = Field(default=None, max_length=255)


class VendorInvoiceItemOut(BaseModel):
    id: int
    invoiceId: int
    itemName: Optional[str] = None
    taxRate: Optional[float] = None
    amountExclTax: float = 0
    taxAmount: float = 0
    amountInclTax: float = 0
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "VendorInvoiceItemOut":
        return cls(
            id=m.id,
            invoiceId=m.invoice_id,
            itemName=m.item_name,
            taxRate=_f(m.tax_rate),
            amountExclTax=_f0(m.amount_excl_tax),
            taxAmount=_f0(m.tax_amount),
            amountInclTax=_f0(m.amount_incl_tax),
            remark=m.remark,
        )


class InvoiceSettleLinkOut(BaseModel):
    """核销明细行"""

    id: int
    invoiceId: int
    settleId: int
    settleDocNo: Optional[str] = None
    appliedAmount: float = 0
    matchedAt: Optional[datetime] = None
    matchedBy: Optional[int] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "InvoiceSettleLinkOut":
        return cls(
            id=m.id,
            invoiceId=m.invoice_id,
            settleId=m.settle_id,
            settleDocNo=m.settle_doc_no,
            appliedAmount=_f0(m.applied_amount),
            matchedAt=m.matched_at,
            matchedBy=m.matched_by,
            remark=m.remark,
        )


class VendorInvoiceListItem(BaseModel):
    """台账列表行"""

    id: int
    docNo: str
    vendorType: int = 1
    vendorTypeLabel: Optional[str] = None
    vendorId: Optional[int] = None
    vendorName: Optional[str] = None
    sellerTitle: Optional[str] = None
    buyerEntityId: Optional[int] = None
    buyerTitle: Optional[str] = None
    invoiceType: int = 2
    invoiceTypeLabel: Optional[str] = None
    invoiceNo: str
    invoiceCode: Optional[str] = None
    invoiceDate: Optional[date] = None
    receivedAt: Optional[datetime] = None
    amountExclTax: float = 0
    taxRate: Optional[float] = None
    taxAmount: float = 0
    amountInclTax: float = 0
    isMultiRate: int = 0
    settledAmount: float = 0
    unsettledAmount: float = 0
    settleCount: int = 0
    deductible: int = 1
    deductPeriod: Optional[str] = None
    verifyStatus: int = 0
    verifyStatusLabel: Optional[str] = None
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "VendorInvoiceListItem":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            vendorType=int(m.vendor_type or 0),
            vendorTypeLabel=VendorType.LABELS.get(int(m.vendor_type or 0)),
            vendorId=m.vendor_id,
            vendorName=m.vendor_name,
            sellerTitle=m.seller_title,
            buyerEntityId=m.buyer_entity_id,
            buyerTitle=m.buyer_title,
            invoiceType=int(m.invoice_type or 0),
            invoiceTypeLabel=InvoiceType.LABELS.get(int(m.invoice_type or 0)),
            invoiceNo=m.invoice_no,
            invoiceCode=m.invoice_code,
            invoiceDate=m.invoice_date,
            receivedAt=m.received_at,
            amountExclTax=_f0(m.amount_excl_tax),
            taxRate=_f(m.tax_rate),
            taxAmount=_f0(m.tax_amount),
            amountInclTax=_f0(m.amount_incl_tax),
            isMultiRate=int(m.is_multi_rate or 0),
            settledAmount=_f0(m.settled_amount),
            unsettledAmount=_f0(m.unsettled_amount),
            settleCount=int(m.settle_count or 0),
            deductible=int(m.deductible or 0),
            deductPeriod=m.deduct_period,
            verifyStatus=int(m.verify_status or 0),
            verifyStatusLabel=VerifyStatus.LABELS.get(int(m.verify_status or 0)),
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _DOC_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class VendorInvoiceOut(VendorInvoiceListItem):
    """详情"""

    sellerTaxNo: Optional[str] = None
    buyerTaxNo: Optional[str] = None
    attachmentUrl: Optional[str] = None
    voidReason: Optional[str] = None
    voidedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    items: List[VendorInvoiceItemOut] = Field(default_factory=list)
    settles: List[InvoiceSettleLinkOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        items: Optional[List[Any]] = None,
        settles: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "VendorInvoiceOut":
        base = VendorInvoiceListItem.from_model(m).model_dump()
        return cls(
            **base,
            sellerTaxNo=m.seller_tax_no,
            buyerTaxNo=m.buyer_tax_no,
            attachmentUrl=m.attachment_url,
            voidReason=m.void_reason,
            voidedAt=m.voided_at,
            cancelReason=m.cancel_reason,
            items=[VendorInvoiceItemOut.from_model(x) for x in (items or [])],
            settles=[InvoiceSettleLinkOut.from_model(x) for x in (settles or [])],
            actions=actions or {},
        )


class VendorInvoiceCreateRequest(BaseModel):
    invoiceNo: str = Field(min_length=1, max_length=50)
    invoiceCode: Optional[str] = Field(default=None, max_length=30)
    invoiceType: int = Field(
        default=InvoiceType.SPECIAL, ge=1, le=5,
        description="1-普票 2-专票 3-电子普票 4-电子专票 5-其他",
    )
    invoiceDate: Optional[date] = None
    receivedAt: Optional[datetime] = None
    vendorType: int = Field(
        default=VendorType.CARRIER, ge=1, le=3,
        description="1-承运商 2-社会运力 3-其他供应商",
    )
    vendorId: Optional[int] = None
    sellerTitle: Optional[str] = Field(default=None, max_length=100)
    sellerTaxNo: Optional[str] = Field(default=None, max_length=30)
    buyerEntityId: Optional[int] = None
    buyerTitle: Optional[str] = Field(default=None, max_length=100)
    buyerTaxNo: Optional[str] = Field(default=None, max_length=30)
    amountExclTax: Optional[Decimal] = None
    taxAmount: Optional[Decimal] = None
    amountInclTax: Optional[Decimal] = None
    taxRate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    deductible: Optional[int] = Field(default=None, ge=0, le=1)
    deductPeriod: Optional[str] = Field(
        default=None, max_length=7, description="抵扣税期 YYYY-MM",
    )
    attachmentUrl: Optional[str] = Field(default=None, max_length=500)
    items: List[VendorInvoiceItemIn] = Field(
        default_factory=list, description="多税率发票才传；传了则主表金额取行汇总",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class VendorInvoiceUpdateRequest(BaseModel):
    invoiceType: Optional[int] = Field(default=None, ge=1, le=5)
    invoiceDate: Optional[date] = None
    sellerTitle: Optional[str] = Field(default=None, max_length=100)
    sellerTaxNo: Optional[str] = Field(default=None, max_length=30)
    buyerEntityId: Optional[int] = None
    buyerTitle: Optional[str] = Field(default=None, max_length=100)
    buyerTaxNo: Optional[str] = Field(default=None, max_length=30)
    amountExclTax: Optional[Decimal] = None
    taxAmount: Optional[Decimal] = None
    amountInclTax: Optional[Decimal] = None
    taxRate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    deductible: Optional[int] = Field(default=None, ge=0, le=1)
    deductPeriod: Optional[str] = Field(default=None, max_length=7)
    attachmentUrl: Optional[str] = Field(default=None, max_length=500)
    items: Optional[List[VendorInvoiceItemIn]] = Field(
        default=None, description="传空数组表示改回单税率",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class InvoiceMatchItemIn(BaseModel):
    settleId: int
    appliedAmount: Decimal = Field(gt=0)
    remark: Optional[str] = Field(default=None, max_length=255)


class InvoiceMatchRequest(BaseModel):
    allocations: List[InvoiceMatchItemIn] = Field(min_length=1)


class InvoiceReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


class DeductSummaryOut(BaseModel):
    groupBy: str
    groupKey: Optional[Any] = None
    invoiceCount: int = 0
    amountExclTax: float = 0
    taxAmount: float = 0
    amountInclTax: float = 0


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
