"""承运商结算单 Schemas

与客户结算单对称，出参多两组应付侧信息：付款账户（脱敏后四位）与进项票收票进度
（已核销票额、缺口金额）。缺口金额是派生值，不建表，见文档 11 §4.3。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import (
    CarrierSettlementType,
    PayMethod,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_SETTLE_KIND = "carrier_settle"


class CarrierSettleReconCandidateOut(BaseModel):
    """可并入结算的已确认对账单"""

    reconId: int
    docNo: str
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    taskCount: int = 0
    grossAmountTotal: float = 0
    prepaidOffsetTotal: float = 0
    plannedAmount: float = 0
    appliedAmountTotal: float = 0
    availableAmount: float = 0
    confirmedByCarrierAt: Optional[datetime] = None
    diffForcedCount: int = 0


class CarrierAccountOut(BaseModel):
    """承运商结算账户（付款账户选择器）"""

    accountId: int
    accountLabel: Optional[str] = None
    accountType: int = 0
    settlementType: int = 0
    settlementTypeLabel: Optional[str] = None
    bankName: Optional[str] = None
    bankAccountMasked: Optional[str] = None
    bankAccountName: Optional[str] = None
    isDefault: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "CarrierAccountOut":
        return cls(
            **d,
            settlementTypeLabel=CarrierSettlementType.LABELS.get(
                int(d.get("settlementType") or 0)
            ),
        )


class CarrierSettleReconLinkOut(BaseModel):
    """结算单关联的对账单行"""

    id: int
    settleId: int
    reconId: int
    reconDocNo: Optional[str] = None
    appliedAmount: float = 0
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "CarrierSettleReconLinkOut":
        return cls(
            id=m.id,
            settleId=m.settle_id,
            reconId=m.recon_id,
            reconDocNo=m.recon_doc_no,
            appliedAmount=_f0(m.applied_amount),
            remark=m.remark,
        )


class SettleInvoiceLinkOut(BaseModel):
    """本单的进项票构成"""

    id: int
    invoiceId: int
    settleId: int
    appliedAmount: float = 0
    matchedAt: Optional[datetime] = None
    matchedBy: Optional[int] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "SettleInvoiceLinkOut":
        return cls(
            id=m.id,
            invoiceId=m.invoice_id,
            settleId=m.settle_id,
            appliedAmount=_f0(m.applied_amount),
            matchedAt=m.matched_at,
            matchedBy=m.matched_by,
            remark=m.remark,
        )


class CarrierSettleListItem(BaseModel):
    """列表行（字段与文档 03 §8.3 对齐）"""

    id: int
    docNo: str
    carrierId: int
    carrierName: Optional[str] = None
    enterpriseId: Optional[int] = None
    reconCount: int = 0
    plannedAmount: float = 0
    paidAmountTotal: float = 0
    unpaidAmount: float = 0
    actualAmount: Optional[float] = None
    paidAt: Optional[datetime] = None
    payMethod: Optional[int] = None
    payMethodLabel: Optional[str] = None
    settlementAccountLabel: Optional[str] = None
    bankAccountMasked: Optional[str] = None
    dueDate: Optional[date] = None
    isOffsetOnly: int = 0
    invoiceMatched: int = 0
    invoiceAmountTotal: float = 0
    invoiceGapAmount: float = 0
    batchId: Optional[int] = None
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "CarrierSettleListItem":
        planned = Decimal(str(m.planned_amount or 0))
        paid = Decimal(str(m.paid_amount_total or 0))
        invoiced = Decimal(str(m.invoice_amount_total or 0))
        return cls(
            id=m.id,
            docNo=m.doc_no,
            carrierId=m.carrier_id,
            carrierName=m.carrier_name,
            enterpriseId=m.enterprise_id,
            reconCount=int(m.recon_count or 0),
            plannedAmount=float(planned),
            paidAmountTotal=float(paid),
            unpaidAmount=float(max(planned - paid, Decimal("0"))),
            actualAmount=_f(m.actual_amount),
            paidAt=m.paid_at,
            payMethod=m.pay_method,
            payMethodLabel=PayMethod.LABELS.get(int(m.pay_method or 0)),
            settlementAccountLabel=m.settlement_account_label,
            bankAccountMasked=m.bank_account_masked,
            dueDate=m.due_date,
            isOffsetOnly=int(m.is_offset_only or 0),
            invoiceMatched=int(m.invoice_matched or 0),
            invoiceAmountTotal=float(invoiced),
            invoiceGapAmount=float(max(planned - invoiced, Decimal("0"))),
            batchId=m.batch_id,
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _SETTLE_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class CarrierSettleOut(CarrierSettleListItem):
    """详情"""

    settlementAccountId: Optional[int] = None
    bankName: Optional[str] = None
    payVoucherUrl: Optional[str] = None
    submittedAt: Optional[datetime] = None
    reviewedBy: Optional[int] = None
    reviewedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    recons: List[CarrierSettleReconLinkOut] = Field(default_factory=list)
    invoices: List[SettleInvoiceLinkOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        recons: Optional[List[Any]] = None,
        invoices: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "CarrierSettleOut":
        base = CarrierSettleListItem.from_model(m).model_dump()
        return cls(
            **base,
            settlementAccountId=m.settlement_account_id,
            bankName=m.bank_name,
            payVoucherUrl=m.pay_voucher_url,
            submittedAt=m.submitted_at,
            reviewedBy=m.reviewed_by,
            reviewedAt=m.reviewed_at,
            cancelReason=m.cancel_reason,
            recons=[
                CarrierSettleReconLinkOut.from_model(x) for x in (recons or [])
            ],
            invoices=[
                SettleInvoiceLinkOut.from_model(x) for x in (invoices or [])
            ],
            actions=actions or {},
        )


class CarrierSettleReconItemIn(BaseModel):
    """关联一张对账单"""

    reconId: int
    appliedAmount: Optional[Decimal] = Field(
        default=None, gt=0, description="认领金额；留空表示认领该对账单全部未结金额",
    )
    remark: Optional[str] = Field(default=None, max_length=255)


class CarrierSettleCreateRequest(BaseModel):
    carrierId: int
    recons: List[CarrierSettleReconItemIn] = Field(min_length=1)
    settlementAccountId: Optional[int] = Field(
        default=None, description="付款账户；留空取承运商默认账户",
    )
    dueDate: Optional[date] = None
    isOffsetOnly: int = Field(
        default=0, ge=0, le=1,
        description="1 表示纯抵账（预付已覆盖全额，不实付、不校验凭证）",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class CarrierSettleUpdateRequest(BaseModel):
    dueDate: Optional[date] = None
    isOffsetOnly: Optional[int] = Field(default=None, ge=0, le=1)
    remark: Optional[str] = Field(default=None, max_length=500)


class CarrierSettleLinkReconsRequest(BaseModel):
    recons: List[CarrierSettleReconItemIn] = Field(min_length=1)


class CarrierSettleAccountRequest(BaseModel):
    settlementAccountId: int


class CarrierSettlePayRequest(BaseModel):
    """付款登记（纯抵账单可只传空对象）"""

    actualAmount: Optional[Decimal] = Field(
        default=None, ge=0, description="实付金额；留空取应付金额",
    )
    paidAt: Optional[datetime] = None
    payMethod: Optional[int] = Field(
        default=None, ge=1, le=6,
        description="1-银行转账 2-油卡 3-油气款 4-现金 5-微信 6-支付宝",
    )
    settlementAccountId: Optional[int] = None
    payVoucherUrl: Optional[str] = Field(default=None, max_length=500)


class CarrierSettleReasonRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=255)


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
