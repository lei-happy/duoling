"""承运商对账单 Schemas

与客户对账单同构，出参多三个应付侧字段：毛额、预付扣减、净额。前端列表要能一眼
看出「毛额多少、已经付过多少、还要付多少」，这三列缺一不可。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import (
    BillingBase,
    CarrierSettlementType,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    label as status_label,
)

_RECON_KIND = "carrier_recon"


class CarrierReconCandidateOut(BaseModel):
    """候选任务行（选择器用，带预付扣减预览）"""

    taskId: int
    taskNo: Optional[str] = None
    plateNumber: Optional[str] = None
    mainDriverName: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    signedQuantity: int = 0
    signedAt: Optional[datetime] = None
    carrierCostAmount: Optional[float] = None
    prepaidOffsetAmount: Optional[float] = None
    netAmount: Optional[float] = None
    status: int = 0


class CarrierReconLineOut(BaseModel):
    """承运商对账行"""

    id: int
    reconId: int
    taskId: int
    taskNo: Optional[str] = None
    plateNumber: Optional[str] = None
    billingBase: int
    billingBaseLabel: Optional[str] = None
    quantity: float = 0
    unitPrice: float = 0
    grossAmount: float = 0
    adjustAmount: float = 0
    adjustReason: Optional[str] = None
    prepaidOffsetAmount: float = 0
    netAmount: float = 0
    carrierCostSnapshot: Optional[float] = None
    signedQuantitySnapshot: Optional[int] = None
    signedAtSnapshot: Optional[datetime] = None
    lockedSnapshotAt: Optional[datetime] = None
    reconDirty: int = 0
    dirtyReason: Optional[str] = None
    dirtyAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "CarrierReconLineOut":
        return cls(
            id=m.id,
            reconId=m.recon_id,
            taskId=m.task_id,
            taskNo=m.task_no,
            plateNumber=m.plate_number,
            billingBase=int(m.billing_base or 0),
            billingBaseLabel=BillingBase.LABELS.get(int(m.billing_base or 0)),
            quantity=_f0(m.quantity),
            unitPrice=_f0(m.unit_price),
            grossAmount=_f0(m.gross_amount),
            adjustAmount=_f0(m.adjust_amount),
            adjustReason=m.adjust_reason,
            prepaidOffsetAmount=_f0(m.prepaid_offset_amount),
            netAmount=_f0(m.net_amount),
            carrierCostSnapshot=_f(m.carrier_cost_snapshot),
            signedQuantitySnapshot=m.signed_quantity_snapshot,
            signedAtSnapshot=m.signed_at_snapshot,
            lockedSnapshotAt=m.locked_snapshot_at,
            reconDirty=int(m.recon_dirty or 0),
            dirtyReason=m.dirty_reason,
            dirtyAt=m.dirty_at,
            remark=m.remark,
        )


class CarrierReconListItem(BaseModel):
    """列表行（字段与文档 03 §8.3 对齐）"""

    id: int
    docNo: str
    carrierId: int
    carrierName: Optional[str] = None
    carrierShortName: Optional[str] = None
    enterpriseId: Optional[int] = None
    periodStart: Optional[datetime] = None
    periodEnd: Optional[datetime] = None
    taskCount: int = 0
    totalQuantity: float = 0
    grossAmountTotal: float = 0
    prepaidOffsetTotal: float = 0
    plannedAmount: float = 0
    adjustAmountTotal: float = 0
    appliedAmountTotal: float = 0
    paidAmountTotal: float = 0
    settleCount: int = 0
    dirtyLineCount: int = 0
    diffOpenCount: int = 0
    diffForcedCount: int = 0
    confirmedByCarrierAt: Optional[datetime] = None
    settlementAccountLabel: Optional[str] = None
    settlementTypeSnapshot: Optional[int] = None
    settlementTypeLabel: Optional[str] = None
    status: int
    statusLabel: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: Optional[datetime] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m: Any) -> "CarrierReconListItem":
        stype = m.settlement_type_snapshot
        return cls(
            id=m.id,
            docNo=m.doc_no,
            carrierId=m.carrier_id,
            carrierName=m.carrier_name,
            carrierShortName=m.carrier_short_name,
            enterpriseId=m.enterprise_id,
            periodStart=m.period_start,
            periodEnd=m.period_end,
            taskCount=int(m.task_count or 0),
            totalQuantity=_f0(m.total_quantity),
            grossAmountTotal=_f0(m.gross_amount_total),
            prepaidOffsetTotal=_f0(m.prepaid_offset_total),
            plannedAmount=_f0(m.planned_amount),
            adjustAmountTotal=_f0(m.adjust_amount_total),
            appliedAmountTotal=_f0(m.applied_amount_total),
            paidAmountTotal=_f0(m.paid_amount_total),
            settleCount=int(m.settle_count or 0),
            dirtyLineCount=int(m.dirty_line_count or 0),
            diffOpenCount=int(m.diff_open_count or 0),
            diffForcedCount=int(m.diff_forced_count or 0),
            confirmedByCarrierAt=m.confirmed_by_carrier_at,
            settlementAccountLabel=m.settlement_account_label,
            settlementTypeSnapshot=stype,
            settlementTypeLabel=(
                CarrierSettlementType.LABELS.get(int(stype))
                if stype is not None else None
            ),
            status=int(m.status or 0),
            statusLabel=status_label(int(m.status or 0), _RECON_KIND),
            createdBy=m.created_by,
            createdAt=m.created_at,
            remark=m.remark,
        )


class CarrierReconOut(CarrierReconListItem):
    """详情（含行与按钮位）"""

    settlementAccountId: Optional[int] = None
    confirmedByCarrierName: Optional[str] = None
    confirmVoucherUrl: Optional[str] = None
    carrierContactName: Optional[str] = None
    carrierContactPhone: Optional[str] = None
    adjustApprovedBy: Optional[int] = None
    adjustApprovedAt: Optional[datetime] = None
    cancelReason: Optional[str] = None
    lines: List[CarrierReconLineOut] = Field(default_factory=list)
    actions: dict = Field(default_factory=dict)

    @classmethod
    def from_model(
        cls,
        m: Any,
        *,
        lines: Optional[List[Any]] = None,
        actions: Optional[dict] = None,
    ) -> "CarrierReconOut":
        base = CarrierReconListItem.from_model(m).model_dump()
        return cls(
            **base,
            settlementAccountId=m.settlement_account_id,
            confirmedByCarrierName=m.confirmed_by_carrier_name,
            confirmVoucherUrl=m.confirm_voucher_url,
            carrierContactName=m.carrier_contact_name,
            carrierContactPhone=m.carrier_contact_phone,
            adjustApprovedBy=m.adjust_approved_by,
            adjustApprovedAt=m.adjust_approved_at,
            cancelReason=m.cancel_reason,
            lines=[CarrierReconLineOut.from_model(x) for x in (lines or [])],
            actions=actions or {},
        )


class CarrierReconCreateRequest(BaseModel):
    """按候选生成草稿对账单"""

    carrierId: int
    periodStart: date
    periodEnd: date
    taskIds: List[int] = Field(default_factory=list)
    billingBase: int = Field(
        default=BillingBase.BY_VEHICLE, ge=1, le=4,
        description="1-按台 2-按吨 3-按趟 4-包车",
    )
    remark: Optional[str] = Field(default=None, max_length=500)


class CarrierReconUpdateRequest(BaseModel):
    """编辑草稿的表头（周期、联系人与备注；换承运商请新建）"""

    periodStart: Optional[date] = None
    periodEnd: Optional[date] = None
    carrierContactName: Optional[str] = Field(default=None, max_length=50)
    carrierContactPhone: Optional[str] = Field(default=None, max_length=20)
    settlementAccountId: Optional[int] = None
    remark: Optional[str] = Field(default=None, max_length=500)


class CarrierReconAddTasksRequest(BaseModel):
    """批量添加对账行"""

    taskIds: List[int] = Field(min_length=1)
    billingBase: int = Field(default=BillingBase.BY_VEHICLE, ge=1, le=4)


class CarrierReconLineAdjustRequest(BaseModel):
    """调整对账行（扣减额不可改，需用调整额补回）"""

    quantity: Optional[Decimal] = Field(default=None, ge=0)
    unitPrice: Optional[Decimal] = Field(default=None, ge=0)
    adjustAmount: Optional[Decimal] = None
    adjustReason: Optional[str] = Field(default=None, max_length=255)
    remark: Optional[str] = None


class CarrierReconConfirmRequest(BaseModel):
    """确认对账单；带 forceReason 时走强制确认（财务主管）"""

    forceReason: Optional[str] = Field(
        default=None, min_length=10, max_length=255,
        description="带未决差异强制确认的原因（不少于 10 个字）",
    )


class CarrierSignRequest(BaseModel):
    """登记承运商回签"""

    signerName: str = Field(min_length=1, max_length=100)
    voucherUrl: Optional[str] = Field(default=None, max_length=500)
    signedAt: Optional[datetime] = None


class CarrierReconReasonRequest(BaseModel):
    """需要原因的动作（退回 / 撤销 / 解锁结清）"""

    reason: str = Field(min_length=5, max_length=255)


class CarrierReconRecalcRequest(BaseModel):
    """回灌重算"""

    onlyDirty: bool = Field(
        default=True, description="只重算脏行；false 表示全部行都按业务侧刷新",
    )


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _f0(v: Any) -> float:
    return float(v) if v is not None else 0.0
