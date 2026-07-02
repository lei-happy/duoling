"""任务单财务费用单 Schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.client.schemas.task.task_finance_item import (
    TaskFinanceItemIn, TaskFinanceItemOut,
)


class TaskFinanceDocCreate(BaseModel):
    """创建费用单（含 items）"""
    docType: int = Field(ge=1, le=4,
                         description="1-预付单 2-补款单 3-结算单 4-承包单")
    isFinal: int = Field(default=0, ge=0, le=1,
                         description="是否最终结算单（仅 doc_type=3 可为 1）")
    payeeType: int = Field(ge=1, le=3, description="1-司机 2-承运商 3-其他")
    payeeId: Optional[int] = None
    payeeName: Optional[str] = None
    payeeAccountType: Optional[int] = None
    payeeAccountId: Optional[int] = None
    payeeBankName: Optional[str] = None
    payeeBankAccountMasked: Optional[str] = None
    plannedAmount: float = Field(gt=0)
    currency: str = "CNY"
    periodStart: Optional[datetime] = Field(
        default=None, description="结算周期起（承包单必填）")
    periodEnd: Optional[datetime] = Field(
        default=None, description="结算周期止（承包单必填）")
    payMethod: Optional[int] = None
    plannedPayTime: Optional[datetime] = None
    remark: Optional[str] = None
    items: List[TaskFinanceItemIn] = Field(default_factory=list)


class TaskFinanceDocUpdate(BaseModel):
    """更新费用单（仅 draft / pending review）"""
    payeeType: Optional[int] = None
    payeeId: Optional[int] = None
    payeeName: Optional[str] = None
    payeeAccountType: Optional[int] = None
    payeeAccountId: Optional[int] = None
    payeeBankName: Optional[str] = None
    payeeBankAccountMasked: Optional[str] = None
    plannedAmount: Optional[float] = None
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    payMethod: Optional[int] = None
    plannedPayTime: Optional[datetime] = None
    isFinal: Optional[int] = None
    remark: Optional[str] = None
    items: Optional[List[TaskFinanceItemIn]] = None


class TaskFinanceDocPayRequest(BaseModel):
    """标记已支付"""
    actualAmount: float = Field(gt=0)
    payMethod: int = Field(ge=1, le=6)
    actualPayTime: datetime
    payVoucherUrl: Optional[str] = None
    remark: Optional[str] = None


class TaskFinanceDocCancelRequest(BaseModel):
    reason: Optional[str] = None


class TaskFinanceDocReasonRequest(BaseModel):
    """需强制填写原因的高权限动作（撤销支付 / 强制撤销）"""
    reason: str = Field(min_length=5, description="原因（不少于 5 个字）")


class TaskFinanceDocBatchActionRequest(BaseModel):
    """批量执行费用单动作（approve / pay / cancel / submit）"""
    ids: List[int] = Field(min_length=1)
    action: str = Field(description="approve | pay | cancel | submit")
    # pay 才需要
    actualAmount: Optional[float] = None
    payMethod: Optional[int] = None
    actualPayTime: Optional[datetime] = None
    payVoucherUrl: Optional[str] = None
    # cancel 才需要
    reason: Optional[str] = None
    remark: Optional[str] = None


class TaskFinanceDocOut(BaseModel):
    id: int
    taskId: int
    docNo: str
    docType: int
    docKind: str = "task_finance"
    direction: int = 2
    isFinal: int
    payeeType: int
    payeeId: Optional[int] = None
    payeeName: Optional[str] = None
    payeeAccountType: Optional[int] = None
    payeeAccountId: Optional[int] = None
    payeeBankName: Optional[str] = None
    payeeBankAccountMasked: Optional[str] = None
    plannedAmount: float
    actualAmount: Optional[float] = None
    currency: str
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    payMethod: Optional[int] = None
    plannedPayTime: Optional[datetime] = None
    actualPayTime: Optional[datetime] = None
    payVoucherUrl: Optional[str] = None
    status: int
    createdBy: Optional[int] = None
    submittedBy: Optional[int] = None
    submittedAt: Optional[datetime] = None
    reviewedBy: Optional[int] = None
    reviewedAt: Optional[datetime] = None
    paidBy: Optional[int] = None
    cancelledBy: Optional[int] = None
    cancelledAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    isLocked: int = 0
    lockedByDocId: Optional[int] = None
    approvalNo: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime
    # 操作能力位（由状态/锁定/单据类型推导，供前端联动按钮）
    canSubmit: bool = False
    canApprove: bool = False
    canPay: bool = False
    canWithdraw: bool = False
    canCancel: bool = False
    canCancelPay: bool = False
    canForceCancel: bool = False
    items: List[TaskFinanceItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, items: Optional[list] = None) -> "TaskFinanceDocOut":
        item_list = [TaskFinanceItemOut.from_model(i) for i in (items or [])]
        status = int(m.status)
        locked = int(getattr(m, "is_locked", 0) or 0) == 1
        return cls(
            id=m.id,
            taskId=m.task_id,
            docNo=m.doc_no,
            docType=m.doc_type,
            docKind=getattr(m, "doc_kind", None) or "task_finance",
            direction=int(getattr(m, "direction", 2) or 2),
            isFinal=m.is_final,
            payeeType=m.payee_type,
            payeeId=m.payee_id,
            payeeName=m.payee_name,
            payeeAccountType=m.payee_account_type,
            payeeAccountId=m.payee_account_id,
            payeeBankName=m.payee_bank_name,
            payeeBankAccountMasked=m.payee_bank_account_masked,
            plannedAmount=float(m.planned_amount),
            actualAmount=float(m.actual_amount) if m.actual_amount is not None else None,
            currency=m.currency,
            periodStart=getattr(m, "period_start", None),
            periodEnd=getattr(m, "period_end", None),
            payMethod=m.pay_method,
            plannedPayTime=m.planned_pay_time,
            actualPayTime=m.actual_pay_time,
            payVoucherUrl=m.pay_voucher_url,
            status=status,
            createdBy=m.created_by,
            submittedBy=getattr(m, "submitted_by", None),
            submittedAt=getattr(m, "submitted_at", None),
            reviewedBy=m.reviewed_by,
            reviewedAt=m.reviewed_at,
            paidBy=m.paid_by,
            cancelledBy=getattr(m, "cancelled_by", None),
            cancelledAt=getattr(m, "cancelled_at", None),
            cancelReason=getattr(m, "cancel_reason", None),
            isLocked=1 if locked else 0,
            lockedByDocId=getattr(m, "locked_by_doc_id", None),
            approvalNo=m.approval_no,
            remark=m.remark,
            createdAt=m.created_at,
            canSubmit=(status == 0 and not locked),
            canApprove=(status == 1 and not locked),
            canPay=(status == 2 and not locked),
            canWithdraw=(status in (1, 2) and not locked),
            canCancel=(status in (0, 1, 2) and not locked),
            canCancelPay=(status == 3),
            canForceCancel=(status == 3),
            items=item_list,
        )


class TaskFinanceDocListItem(BaseModel):
    """费用单列表行（不带 items）"""
    id: int
    taskId: int
    taskNo: Optional[str] = None
    docNo: str
    docType: int
    isFinal: int
    payeeType: int
    payeeName: Optional[str] = None
    plannedAmount: float
    actualAmount: Optional[float] = None
    payMethod: Optional[int] = None
    status: int
    createdAt: datetime
    plannedPayTime: Optional[datetime] = None
    actualPayTime: Optional[datetime] = None
