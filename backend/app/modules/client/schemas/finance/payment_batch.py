"""打款批次 Schemas"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import (
    BatchExecStatus,
    PayableDocKind,
    PayMethod,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_DOC_KIND = "payment_batch"


class PayableCandidateOut(BaseModel):
    """可入批的应付单"""

    docKind: str
    docKindLabel: Optional[str] = None
    docId: int
    docNo: Optional[str] = None
    amount: float = 0
    payeeType: int = 3
    payeeId: Optional[int] = None
    payeeName: Optional[str] = None
    payeeBankName: Optional[str] = None
    payeeBankAccount: Optional[str] = None
    dueDate: Optional[date] = None
    reviewedAt: Optional[datetime] = None
    remark: Optional[str] = None


class PaymentBatchItemOut(BaseModel):
    id: int
    batchId: int
    docKind: str
    docKindLabel: Optional[str] = None
    docId: int
    docNo: Optional[str] = None
    payeeType: int = 3
    payeeId: Optional[int] = None
    payeeName: Optional[str] = None
    payeeBankName: Optional[str] = None
    payeeBankAccount: Optional[str] = None
    amount: float = 0
    payMethod: Optional[int] = None
    payMethodLabel: Optional[str] = None
    execStatus: int = 0
    execStatusLabel: Optional[str] = None
    failReason: Optional[str] = None
    bankSerialNo: Optional[str] = None
    paidAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "PaymentBatchItemOut":
        return cls(
            id=m.id,
            batchId=m.batch_id,
            docKind=m.doc_kind,
            docKindLabel=PayableDocKind.LABELS.get(m.doc_kind),
            docId=m.doc_id,
            docNo=m.doc_no,
            payeeType=int(m.payee_type or 0),
            payeeId=m.payee_id,
            payeeName=m.payee_name,
            payeeBankName=m.payee_bank_name,
            payeeBankAccount=m.payee_bank_account,
            amount=float(m.amount or 0),
            payMethod=m.pay_method,
            payMethodLabel=PayMethod.LABELS.get(int(m.pay_method or 0)),
            execStatus=int(m.exec_status or 0),
            execStatusLabel=BatchExecStatus.LABELS.get(int(m.exec_status or 0)),
            failReason=m.fail_reason,
            bankSerialNo=m.bank_serial_no,
            paidAt=m.paid_at,
            remark=m.remark,
        )


class PaymentBatchListItem(BaseModel):
    id: int
    docNo: str
    status: int
    statusLabel: Optional[str] = None
    enterpriseId: Optional[int] = None
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = None
    payMethod: Optional[int] = None
    payMethodLabel: Optional[str] = None
    itemCount: int = 0
    successCount: int = 0
    failCount: int = 0
    totalAmount: float = 0
    paidAmount: float = 0
    planPayDate: Optional[date] = None
    execStartedAt: Optional[datetime] = None
    execFinishedAt: Optional[datetime] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "PaymentBatchListItem":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _DOC_KIND),
            enterpriseId=m.enterprise_id,
            bankAccountId=m.bank_account_id,
            bankAccountLabel=m.bank_account_label,
            payMethod=m.pay_method,
            payMethodLabel=PayMethod.LABELS.get(int(m.pay_method or 0)),
            itemCount=int(m.item_count or 0),
            successCount=int(m.success_count or 0),
            failCount=int(m.fail_count or 0),
            totalAmount=float(m.total_amount or 0),
            paidAmount=float(m.paid_amount or 0),
            planPayDate=m.plan_pay_date,
            execStartedAt=m.exec_started_at,
            execFinishedAt=m.exec_finished_at,
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class PaymentBatchOut(PaymentBatchListItem):
    cancelReason: Optional[str] = None
    items: List[PaymentBatchItemOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        items: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "PaymentBatchOut":
        base = PaymentBatchListItem.from_model(m).model_dump()
        return cls(
            **base,
            cancelReason=m.cancel_reason,
            items=[PaymentBatchItemOut.from_model(x) for x in (items or [])],
            actions=actions or {},
        )


class PayableDocIn(BaseModel):
    docKind: str = Field(description="task_finance / carrier_settle / driver_payroll")
    docId: int


class PaymentBatchCreateRequest(BaseModel):
    docs: List[PayableDocIn] = Field(min_length=1)
    bankAccountId: Optional[int] = None
    enterpriseId: Optional[int] = None
    payMethod: int = Field(default=PayMethod.BANK_TRANSFER, ge=1, le=6)
    planPayDate: Optional[date] = None
    remark: Optional[str] = Field(default=None, max_length=500)


class PaymentBatchUpdateRequest(BaseModel):
    bankAccountId: Optional[int] = None
    payMethod: Optional[int] = Field(default=None, ge=1, le=6)
    planPayDate: Optional[date] = None
    remark: Optional[str] = Field(default=None, max_length=500)


class PaymentBatchAddItemsRequest(BaseModel):
    docs: List[PayableDocIn] = Field(min_length=1)


class BatchExecItemIn(BaseModel):
    itemId: int
    success: bool = True
    bankSerialNo: Optional[str] = Field(default=None, max_length=64)
    paidAt: Optional[datetime] = None
    payMethod: Optional[int] = Field(default=None, ge=1, le=6)
    failReason: Optional[str] = Field(default=None, max_length=255)


class PaymentBatchExecuteRequest(BaseModel):
    results: List[BatchExecItemIn] = Field(
        default_factory=list,
        description="留空表示全部打款成功",
    )
    paidAt: Optional[datetime] = None


class PaymentBatchReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


class FundFlowOut(BaseModel):
    """资金流水一行（收付合并视图）"""

    flowId: str
    direction: int = Field(description="1-收款 2-付款")
    docKind: Optional[str] = None
    docKindLabel: Optional[str] = None
    docId: Optional[int] = None
    docNo: Optional[str] = None
    batchId: Optional[int] = None
    batchDocNo: Optional[str] = None
    counterparty: Optional[str] = None
    amount: float = 0
    method: Optional[int] = None
    methodLabel: Optional[str] = None
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = None
    bankSerialNo: Optional[str] = None
    occurredAt: Optional[datetime] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class PayCalendarDayOut(BaseModel):
    date: date
    batchCount: int = 0
    batchAmount: float = 0
    docCount: int = 0
    docAmount: float = 0
    totalAmount: float = 0
