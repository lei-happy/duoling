"""收款单 Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import ReceiveMethod
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_RECEIPT_KIND = "receipt_voucher"


class ReceiptSettleLinkOut(BaseModel):
    """核销明细行"""

    id: int
    receiptId: int
    settleId: int
    settleDocNo: Optional[str] = None
    appliedAmount: float = 0
    settledAt: Optional[datetime] = None
    settledBy: Optional[int] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "ReceiptSettleLinkOut":
        return cls(
            id=m.id,
            receiptId=m.receipt_id,
            settleId=m.settle_id,
            settleDocNo=m.settle_doc_no,
            appliedAmount=_f0(m.applied_amount),
            settledAt=m.settled_at,
            settledBy=m.settled_by,
            remark=m.remark,
        )


class ReceiptListItem(BaseModel):
    """列表行（出纳台「待认领到账」用同一结构）"""

    id: int
    docNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    payerName: Optional[str] = None
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = None
    receivedAt: Optional[datetime] = None
    receiveMethod: Optional[int] = None
    receiveMethodLabel: Optional[str] = None
    bankSerialNo: Optional[str] = None
    plannedAmount: float = 0
    settledAmount: float = 0
    unsettledAmount: float = 0
    voucherUrl: Optional[str] = None
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "ReceiptListItem":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            payerName=m.payer_name,
            bankAccountId=m.bank_account_id,
            bankAccountLabel=m.bank_account_label,
            receivedAt=m.received_at,
            receiveMethod=m.receive_method,
            receiveMethodLabel=ReceiveMethod.LABELS.get(int(m.receive_method or 0)),
            bankSerialNo=m.bank_serial_no,
            plannedAmount=_f0(m.planned_amount),
            settledAmount=_f0(m.settled_amount),
            unsettledAmount=_f0(m.unsettled_amount),
            voucherUrl=m.voucher_url,
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _RECEIPT_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class ReceiptOut(ReceiptListItem):
    """详情"""

    cancelReason: Optional[str] = None
    links: List[ReceiptSettleLinkOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        links: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "ReceiptOut":
        base = ReceiptListItem.from_model(m).model_dump()
        return cls(
            **base,
            cancelReason=m.cancel_reason,
            links=[ReceiptSettleLinkOut.from_model(x) for x in (links or [])],
            actions=actions or {},
        )


class ReceiptClaimCandidateOut(BaseModel):
    """可核销的结算单候选"""

    settleId: int
    docNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    plannedAmount: float = 0
    receivedAmountTotal: float = 0
    unreceivedAmount: float = 0
    appliedByThisReceipt: float = 0
    dueDate: Optional[date] = None


class ReceiptCreateRequest(BaseModel):
    amount: Decimal = Field(gt=0, description="到账金额")
    receivedAt: datetime
    receiveMethod: Optional[int] = Field(default=None, ge=1, le=5)
    customerId: Optional[int] = Field(
        default=None, description="付款客户；认领前不确定可留空",
    )
    payerName: Optional[str] = Field(
        default=None, max_length=100, description="银行回单上的付款方名称",
    )
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = Field(default=None, max_length=100)
    bankSerialNo: Optional[str] = Field(default=None, max_length=64)
    voucherUrl: Optional[str] = Field(default=None, max_length=500)
    remark: Optional[str] = Field(default=None, max_length=500)


class ReceiptUpdateRequest(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    receivedAt: Optional[datetime] = None
    receiveMethod: Optional[int] = Field(default=None, ge=1, le=5)
    customerId: Optional[int] = None
    payerName: Optional[str] = Field(default=None, max_length=100)
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = Field(default=None, max_length=100)
    bankSerialNo: Optional[str] = Field(default=None, max_length=64)
    voucherUrl: Optional[str] = Field(default=None, max_length=500)
    remark: Optional[str] = Field(default=None, max_length=500)


class ReceiptAllocationIn(BaseModel):
    """一条核销分配"""

    settleId: int
    amount: Decimal = Field(
        gt=0, description="核销到该结算单的目标金额（重复提交为覆盖，不累加）",
    )
    remark: Optional[str] = Field(default=None, max_length=255)


class ReceiptClaimRequest(BaseModel):
    allocations: List[ReceiptAllocationIn] = Field(min_length=1)


class ReceiptUnclaimRequest(BaseModel):
    settleId: int
    reason: Optional[str] = Field(default=None, max_length=255)


class ReceiptReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
