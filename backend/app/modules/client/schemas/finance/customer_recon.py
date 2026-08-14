"""客户对账单 Schemas

出参一律带上枚举中文名与动作可用标记（``actions``），前端不再维护一份状态字典，
也不用自己推「这个状态能点哪些按钮」——按钮位由状态机决定，与角色权限是与的关系。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import BillingBase
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_RECON_KIND = "customer_recon"


class ReconCandidateOut(BaseModel):
    """候选运单行（选择器用）"""

    waybillId: int
    waybillNo: Optional[str] = None
    customerId: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    dealerName: Optional[str] = None
    quantity: int = 0
    signedQuantity: int = 0
    signedAt: Optional[datetime] = None
    freightAmount: Optional[float] = None
    status: int = 0


class ReconLineOut(BaseModel):
    """对账行"""

    id: int
    reconId: int
    waybillId: int
    waybillNo: Optional[str] = None
    billingBase: int
    billingBaseLabel: Optional[str] = None
    quantity: float = 0
    unitPrice: float = 0
    amount: float = 0
    adjustAmount: float = 0
    adjustReason: Optional[str] = None
    freightAmountSnapshot: Optional[float] = None
    signedQuantitySnapshot: Optional[int] = None
    lockedSnapshotAt: Optional[datetime] = None
    reconDirty: int = 0
    dirtyReason: Optional[str] = None
    dirtyAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "ReconLineOut":
        return cls(
            id=m.id,
            reconId=m.recon_id,
            waybillId=m.waybill_id,
            waybillNo=m.waybill_no,
            billingBase=int(m.billing_base or 0),
            billingBaseLabel=BillingBase.LABELS.get(int(m.billing_base or 0)),
            quantity=_f0(m.quantity),
            unitPrice=_f0(m.unit_price),
            amount=_f0(m.amount),
            adjustAmount=_f0(m.adjust_amount),
            adjustReason=m.adjust_reason,
            freightAmountSnapshot=_f(m.freight_amount_snapshot),
            signedQuantitySnapshot=m.signed_quantity_snapshot,
            lockedSnapshotAt=m.locked_snapshot_at,
            reconDirty=int(m.recon_dirty or 0),
            dirtyReason=m.dirty_reason,
            dirtyAt=m.dirty_at,
            remark=m.remark,
        )


class ReconListItem(BaseModel):
    """列表行（字段与文档 02 §8.3 对齐）"""

    id: int
    docNo: str
    customerId: int
    customerName: Optional[str] = None
    enterpriseId: Optional[int] = None
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    waybillCount: int = 0
    totalQuantity: float = 0
    plannedAmount: float = 0
    adjustAmountTotal: float = 0
    appliedAmountTotal: float = 0
    receivedAmountTotal: float = 0
    settleCount: int = 0
    dirtyLineCount: int = 0
    diffOpenCount: int = 0
    diffForcedCount: int = 0
    confirmedByCustomerAt: Optional[datetime] = None
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "ReconListItem":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            enterpriseId=m.enterprise_id,
            periodStart=m.period_start,
            periodEnd=m.period_end,
            waybillCount=int(m.waybill_count or 0),
            totalQuantity=_f0(m.total_quantity),
            plannedAmount=_f0(m.planned_amount),
            adjustAmountTotal=_f0(m.adjust_amount_total),
            appliedAmountTotal=_f0(m.applied_amount_total),
            receivedAmountTotal=_f0(m.received_amount_total),
            settleCount=int(m.settle_count or 0),
            dirtyLineCount=int(m.dirty_line_count or 0),
            diffOpenCount=int(m.diff_open_count or 0),
            diffForcedCount=int(m.diff_forced_count or 0),
            confirmedByCustomerAt=m.confirmed_by_customer_at,
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _RECON_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class ReconOut(ReconListItem):
    """详情（含行与按钮位）"""

    settlementType: Optional[int] = None
    confirmedByCustomerName: Optional[str] = None
    confirmVoucherUrl: Optional[str] = None
    customerContactName: Optional[str] = None
    customerContactPhone: Optional[str] = None
    adjustApprovedBy: Optional[int] = None
    adjustApprovedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    lines: List[ReconLineOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        lines: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "ReconOut":
        base = ReconListItem.from_model(m).model_dump()
        return cls(
            **base,
            settlementType=m.settlement_type,
            confirmedByCustomerName=m.confirmed_by_customer_name,
            confirmVoucherUrl=m.confirm_voucher_url,
            customerContactName=m.customer_contact_name,
            customerContactPhone=m.customer_contact_phone,
            adjustApprovedBy=m.adjust_approved_by,
            adjustApprovedAt=m.adjust_approved_at,
            cancelReason=m.cancel_reason,
            lines=[ReconLineOut.from_model(x) for x in (lines or [])],
            actions=actions or {},
        )


class ReconCreateRequest(BaseModel):
    """按候选生成草稿对账单"""

    customerId: int
    periodStart: date
    periodEnd: date
    waybillIds: List[int] = Field(default_factory=list)
    billingBase: int = Field(
        default=BillingBase.BY_VEHICLE, ge=1, le=4,
        description="1-按台 2-按吨 3-按趟 4-固定金额",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class ReconUpdateRequest(BaseModel):
    """编辑草稿的表头（周期与备注；客户不可改，换客户请新建）"""

    periodStart: Optional[date] = None
    periodEnd: Optional[date] = None
    customerContactName: Optional[str] = Field(default=None, max_length=50)
    customerContactPhone: Optional[str] = Field(default=None, max_length=20)
    remark: Optional[str] = Field(default=None, max_length=500)


class ReconAddWaybillsRequest(BaseModel):
    """批量添加对账行"""

    waybillIds: List[int] = Field(min_length=1)
    billingBase: int = Field(default=BillingBase.BY_VEHICLE, ge=1, le=4)


class ReconLineAdjustRequest(BaseModel):
    """调整对账行"""

    quantity: Optional[Decimal] = Field(default=None, ge=0)
    unitPrice: Optional[Decimal] = Field(default=None, ge=0)
    adjustAmount: Optional[Decimal] = None
    adjustReason: Optional[str] = Field(default=None, max_length=255)
    remark: Optional[str] = None


class ReconConfirmRequest(BaseModel):
    """确认对账单；带 forceReason 时走强制确认（财务主管）"""

    forceReason: Optional[str] = Field(
        default=None, min_length=10, max_length=255,
        description="带未决差异强制确认的原因（不少于 10 个字）",
    )


class ReconCustomerSignRequest(BaseModel):
    """登记客户回签"""

    signerName: str = Field(min_length=1, max_length=100)
    voucherUrl: Optional[str] = Field(default=None, max_length=500)
    signedAt: Optional[datetime] = None


class ReconReasonRequest(BaseModel):
    """需要原因的动作（退回 / 撤销 / 解锁结清）"""

    reason: str = Field(min_length=5, max_length=255)


class ReconRecalcRequest(BaseModel):
    """回灌重算"""

    onlyDirty: bool = Field(
        default=True, description="只重算脏行；false 表示全部行都按业务侧刷新",
    )


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
