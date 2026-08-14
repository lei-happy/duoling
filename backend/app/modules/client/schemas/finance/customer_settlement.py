"""客户结算单 Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import ReceiveMethod
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_SETTLE_KIND = "customer_settle"


class SettleReconCandidateOut(BaseModel):
    """可并入结算的已确认对账单"""

    reconId: int
    docNo: str
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    waybillCount: int = 0
    plannedAmount: float = 0
    appliedAmountTotal: float = 0
    availableAmount: float = 0
    confirmedByCustomerAt: Optional[datetime] = None
    diffForcedCount: int = 0


class SettleReconLinkOut(BaseModel):
    """结算单关联的对账单行"""

    id: int
    settleId: int
    reconId: int
    reconDocNo: Optional[str] = None
    appliedAmount: float = 0
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "SettleReconLinkOut":
        return cls(
            id=m.id,
            settleId=m.settle_id,
            reconId=m.recon_id,
            reconDocNo=m.recon_doc_no,
            appliedAmount=_f0(m.applied_amount),
            remark=m.remark,
        )


class SettleReceiptLinkOut(BaseModel):
    """本单的到账构成（收款单核销明细）"""

    id: int
    receiptId: int
    settleId: int
    appliedAmount: float = 0
    settledAt: Optional[datetime] = None
    settledBy: Optional[int] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "SettleReceiptLinkOut":
        return cls(
            id=m.id,
            receiptId=m.receipt_id,
            settleId=m.settle_id,
            appliedAmount=_f0(m.applied_amount),
            settledAt=m.settled_at,
            settledBy=m.settled_by,
            remark=m.remark,
        )


class SettleListItem(BaseModel):
    """列表行"""

    id: int
    docNo: str
    customerId: int
    customerName: Optional[str] = None
    enterpriseId: Optional[int] = None
    reconCount: int = 0
    plannedAmount: float = 0
    receivedAmountTotal: float = 0
    unreceivedAmount: float = 0
    actualAmount: Optional[float] = None
    receivedAt: Optional[datetime] = None
    payMethod: Optional[int] = None
    payMethodLabel: Optional[str] = None
    receivedAccountLabel: Optional[str] = None
    dueDate: Optional[date] = None
    invoiceRequired: int = 0
    invoiceCount: int = 0
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "SettleListItem":
        planned = Decimal(str(m.planned_amount or 0))
        received = Decimal(str(m.received_amount_total or 0))
        return cls(
            id=m.id,
            docNo=m.doc_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            enterpriseId=m.enterprise_id,
            reconCount=int(m.recon_count or 0),
            plannedAmount=float(planned),
            receivedAmountTotal=float(received),
            unreceivedAmount=float(max(planned - received, Decimal("0"))),
            actualAmount=_f(m.actual_amount),
            receivedAt=m.received_at,
            payMethod=m.pay_method,
            payMethodLabel=ReceiveMethod.LABELS.get(int(m.pay_method or 0)),
            receivedAccountLabel=m.received_account_label,
            dueDate=m.due_date,
            invoiceRequired=int(m.invoice_required or 0),
            invoiceCount=int(m.invoice_count or 0),
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _SETTLE_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class SettleOut(SettleListItem):
    """详情"""

    receivedAccountId: Optional[int] = None
    receivedVoucherUrl: Optional[str] = None
    invoiceAmountTotal: float = 0
    submittedAt: Optional[datetime] = None
    reviewedBy: Optional[int] = None
    reviewedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    recons: List[SettleReconLinkOut] = Field(default_factory=list)
    receipts: List[SettleReceiptLinkOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        recons: Optional[List[Any]] = None,
        receipts: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "SettleOut":
        base = SettleListItem.from_model(m).model_dump()
        return cls(
            **base,
            receivedAccountId=m.received_account_id,
            receivedVoucherUrl=m.received_voucher_url,
            invoiceAmountTotal=_f0(m.invoice_amount_total),
            submittedAt=m.submitted_at,
            reviewedBy=m.reviewed_by,
            reviewedAt=m.reviewed_at,
            cancelReason=m.cancel_reason,
            recons=[SettleReconLinkOut.from_model(x) for x in (recons or [])],
            receipts=[SettleReceiptLinkOut.from_model(x) for x in (receipts or [])],
            actions=actions or {},
        )


class SettleReconItemIn(BaseModel):
    """关联一张对账单"""

    reconId: int
    appliedAmount: Optional[Decimal] = Field(
        default=None, gt=0, description="认领金额；留空表示认领该对账单全部未结金额",
    )
    remark: Optional[str] = Field(default=None, max_length=255)


class SettleCreateRequest(BaseModel):
    customerId: int
    recons: List[SettleReconItemIn] = Field(min_length=1)
    dueDate: Optional[date] = Field(
        default=None, description="单据级账期覆盖；留空按客户账期推导",
    )
    invoiceRequired: int = Field(default=0, ge=0, le=1)
    remark: Optional[str] = Field(default=None, max_length=500)


class SettleUpdateRequest(BaseModel):
    dueDate: Optional[date] = None
    invoiceRequired: Optional[int] = Field(default=None, ge=0, le=1)
    remark: Optional[str] = Field(default=None, max_length=500)


class SettleLinkReconsRequest(BaseModel):
    recons: List[SettleReconItemIn] = Field(min_length=1)


class SettleReceiveRequest(BaseModel):
    """单据直登收款"""

    actualAmount: Decimal = Field(gt=0, description="收款金额")
    receivedAt: datetime
    receiveMethod: int = Field(
        ge=1, le=5, description="1-银行转账 2-现金 3-支票 4-承兑汇票 5-平台代收",
    )
    receivedAccountId: Optional[int] = None
    receivedAccountLabel: Optional[str] = Field(default=None, max_length=100)
    voucherUrl: Optional[str] = Field(default=None, max_length=500)


class SettleReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
