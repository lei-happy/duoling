"""司机工资单 Schemas

列表行按文档 04 §7.3 的列清单给足：提成、应发、扣减、抵账、实发五个金额一次返回，
前端不做二次口算——工资单最怕的就是页面上加总跟后端不一致。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import (
    BillingBase,
    PayMethod,
    PayrollItemCategory,
    PayrollModel,
    PayrollPeriodType,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_DOC_KIND = "driver_payroll"

_ACCOUNT_TYPE_LABELS = {1: "银行卡", 2: "油气款", 3: "积分"}


class PayrollCandidateOut(BaseModel):
    """候选任务行"""

    taskId: int
    taskNo: Optional[str] = None
    plateNumber: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    signedQuantity: int = 0
    signedAt: Optional[datetime] = None
    prepaidPaidAmount: Optional[float] = None
    status: int = 0


class DriverAccountOut(BaseModel):
    """司机账户（发薪账户下拉）"""

    accountId: int
    accountType: int = 0
    accountTypeLabel: Optional[str] = None
    accountName: Optional[str] = None
    accountNoMasked: Optional[str] = None
    balance: Optional[float] = None

    @classmethod
    def from_dict(cls, d: dict) -> "DriverAccountOut":
        return cls(
            **d,
            accountTypeLabel=_ACCOUNT_TYPE_LABELS.get(
                int(d.get("accountType") or 0)
            ),
        )


class PayrollTaskLinkOut(BaseModel):
    """任务提成行"""

    id: int
    payrollId: int
    taskId: int
    taskNo: Optional[str] = None
    plateNumber: Optional[str] = None
    signedAt: Optional[datetime] = None
    billingBase: int = 1
    billingBaseLabel: Optional[str] = None
    quantity: float = 0
    unitPrice: float = 0
    commissionAmount: float = 0
    adjustAmount: float = 0
    adjustReason: Optional[str] = None
    signedQuantitySnapshot: Optional[int] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "PayrollTaskLinkOut":
        return cls(
            id=m.id,
            payrollId=m.payroll_id,
            taskId=m.task_id,
            taskNo=m.task_no,
            plateNumber=m.plate_number,
            signedAt=m.signed_at,
            billingBase=int(m.billing_base or 0),
            billingBaseLabel=BillingBase.LABELS.get(int(m.billing_base or 0)),
            quantity=_f0(m.quantity),
            unitPrice=_f0(m.unit_price),
            commissionAmount=_f0(m.commission_amount),
            adjustAmount=_f0(m.adjust_amount),
            adjustReason=m.adjust_reason,
            signedQuantitySnapshot=m.signed_quantity_snapshot,
            remark=m.remark,
        )


class PayrollItemOut(BaseModel):
    """工资项"""

    id: int
    payrollId: int
    itemType: str
    itemName: Optional[str] = None
    category: int = 1
    categoryLabel: Optional[str] = None
    amount: float = 0
    formula: Optional[str] = None
    sortOrder: int = 0
    remark: Optional[str] = None
    isSystem: bool = False

    @classmethod
    def from_model(cls, m: Any) -> "PayrollItemOut":
        return cls(
            id=m.id,
            payrollId=m.payroll_id,
            itemType=m.item_type,
            itemName=m.item_name,
            category=int(m.category or 1),
            categoryLabel=PayrollItemCategory.LABELS.get(int(m.category or 1)),
            amount=_f0(m.amount),
            formula=m.formula,
            sortOrder=int(m.sort_order or 0),
            remark=m.remark,
            isSystem=(m.item_type == "commission_total"),
        )


class PayrollListItem(BaseModel):
    """列表行"""

    id: int
    docNo: str
    driverId: int
    driverName: Optional[str] = None
    driverPhone: Optional[str] = None
    enterpriseId: Optional[int] = None
    payrollModel: int = 3
    payrollModelLabel: Optional[str] = None
    periodType: int = 1
    periodTypeLabel: Optional[str] = None
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    taskCount: int = 0
    totalSignedQuantity: int = 0
    totalCommissionAmount: float = 0
    totalBaseAmount: float = 0
    totalDeductionAmount: float = 0
    totalPrepaidOffsetAmount: float = 0
    grossAmount: float = 0
    netAmount: float = 0
    actualAmount: Optional[float] = None
    paidAt: Optional[datetime] = None
    payMethod: Optional[int] = None
    payMethodLabel: Optional[str] = None
    accountType: Optional[int] = None
    accountTypeLabel: Optional[str] = None
    accountNoMasked: Optional[str] = None
    batchId: Optional[int] = None
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "PayrollListItem":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            driverId=m.driver_id,
            driverName=m.driver_name,
            driverPhone=m.driver_phone,
            enterpriseId=m.enterprise_id,
            payrollModel=int(m.payroll_model or 0),
            payrollModelLabel=PayrollModel.LABELS.get(int(m.payroll_model or 0)),
            periodType=int(m.period_type or 0),
            periodTypeLabel=PayrollPeriodType.LABELS.get(int(m.period_type or 0)),
            periodStart=m.period_start,
            periodEnd=m.period_end,
            taskCount=int(m.task_count or 0),
            totalSignedQuantity=int(m.total_signed_quantity or 0),
            totalCommissionAmount=_f0(m.total_commission_amount),
            totalBaseAmount=_f0(m.total_base_amount),
            totalDeductionAmount=_f0(m.total_deduction_amount),
            totalPrepaidOffsetAmount=_f0(m.total_prepaid_offset_amount),
            grossAmount=_f0(m.gross_amount),
            netAmount=_f0(m.net_amount),
            actualAmount=_f(m.actual_amount),
            paidAt=m.paid_at,
            payMethod=m.pay_method,
            payMethodLabel=PayMethod.LABELS.get(int(m.pay_method or 0)),
            accountType=m.account_type,
            accountTypeLabel=_ACCOUNT_TYPE_LABELS.get(int(m.account_type or 0)),
            accountNoMasked=m.account_no_masked,
            batchId=m.batch_id,
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _DOC_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class PayrollOut(PayrollListItem):
    """详情"""

    accountId: Optional[int] = None
    accountNameSnapshot: Optional[str] = None
    payVoucherUrl: Optional[str] = None
    payslipPdfUrl: Optional[str] = None
    adjustApprovedBy: Optional[int] = None
    adjustApprovedAt: Optional[datetime] = None
    submittedAt: Optional[datetime] = None
    reviewedBy: Optional[int] = None
    reviewedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    tasks: List[PayrollTaskLinkOut] = Field(default_factory=list)
    items: List[PayrollItemOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        tasks: Optional[List[Any]] = None,
        items: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "PayrollOut":
        base = PayrollListItem.from_model(m).model_dump()
        return cls(
            **base,
            accountId=m.account_id,
            accountNameSnapshot=m.account_name_snapshot,
            payVoucherUrl=m.pay_voucher_url,
            payslipPdfUrl=m.payslip_pdf_url,
            adjustApprovedBy=m.adjust_approved_by,
            adjustApprovedAt=m.adjust_approved_at,
            submittedAt=m.submitted_at,
            reviewedBy=m.reviewed_by,
            reviewedAt=m.reviewed_at,
            cancelReason=m.cancel_reason,
            tasks=[PayrollTaskLinkOut.from_model(x) for x in (tasks or [])],
            items=[PayrollItemOut.from_model(x) for x in (items or [])],
            actions=actions or {},
        )


class PayrollCreateRequest(BaseModel):
    driverId: int
    periodStart: date
    periodEnd: date
    taskIds: List[int] = Field(default_factory=list)
    payrollModel: int = Field(
        default=PayrollModel.MIXED, ge=1, le=3,
        description="1-月薪固定 2-计件提成 3-底薪加提成",
    )
    periodType: int = Field(
        default=PayrollPeriodType.MONTHLY, ge=1, le=3,
        description="1-月薪 2-周薪 3-趟薪",
    )
    unitPrice: Optional[Decimal] = Field(
        default=None, ge=0, description="本单统一计件单价；留空建 0 元行后再逐条调整",
    )
    billingBase: int = Field(default=BillingBase.BY_VEHICLE, ge=1, le=4)
    accountId: Optional[int] = Field(
        default=None, description="发薪账户；留空取该司机首个可用账户",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class PayrollUpdateRequest(BaseModel):
    payrollModel: Optional[int] = Field(default=None, ge=1, le=3)
    periodType: Optional[int] = Field(default=None, ge=1, le=3)
    remark: Optional[str] = Field(default=None, max_length=500)


class PayrollAddTasksRequest(BaseModel):
    taskIds: List[int] = Field(min_length=1)
    unitPrice: Optional[Decimal] = Field(default=None, ge=0)
    billingBase: int = Field(default=BillingBase.BY_VEHICLE, ge=1, le=4)


class PayrollTaskAdjustRequest(BaseModel):
    quantity: Optional[Decimal] = Field(default=None, ge=0)
    unitPrice: Optional[Decimal] = Field(default=None, ge=0)
    adjustAmount: Optional[Decimal] = None
    adjustReason: Optional[str] = Field(default=None, max_length=255)
    remark: Optional[str] = None


class PayrollItemCreateRequest(BaseModel):
    itemType: str = Field(min_length=1, max_length=30)
    amount: Decimal = Field(gt=0, description="金额填正数，加减由项目类型决定")
    itemName: Optional[str] = Field(default=None, max_length=50)
    category: Optional[int] = Field(
        default=None, ge=1, le=3,
        description="1-应发项 2-扣减项 3-抵账项；标准项可不传，按字典默认",
    )
    formula: Optional[str] = Field(default=None, max_length=255)
    sortOrder: int = 0
    remark: Optional[str] = Field(default=None, max_length=255)


class PayrollItemUpdateRequest(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    itemName: Optional[str] = Field(default=None, max_length=50)
    formula: Optional[str] = Field(default=None, max_length=255)
    sortOrder: Optional[int] = None
    remark: Optional[str] = Field(default=None, max_length=255)


class PayrollAccountRequest(BaseModel):
    accountId: int


class PayrollPayRequest(BaseModel):
    actualAmount: Optional[Decimal] = Field(
        default=None, description="实发金额；留空取实发合计",
    )
    paidAt: Optional[datetime] = None
    payMethod: Optional[int] = Field(default=None, ge=1, le=6)
    accountId: Optional[int] = None
    payVoucherUrl: Optional[str] = Field(default=None, max_length=500)


class PayrollReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
