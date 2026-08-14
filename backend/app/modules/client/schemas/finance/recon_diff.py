"""对账差异 Schemas

差异是给对账岗看的待办，因此出参里把「快照值 → 当前值」拆成两个字段，并带上
类型与严重度的中文名——前端不需要再维护一份枚举字典，也避免两端翻译不一致。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.recon.diff_constants import (
    BizDocType,
    DiffSeverity,
    DiffStatus,
    DiffType,
)


class ReconDiffOut(BaseModel):
    """差异明细行"""

    id: int
    reconKind: str
    reconId: Optional[int] = None
    linkId: Optional[int] = None
    bizDocType: int
    bizDocTypeLabel: Optional[str] = None
    bizDocId: int
    bizDocNo: Optional[str] = None
    diffType: int
    diffTypeLabel: Optional[str] = None
    severity: int
    severityLabel: Optional[str] = None
    expectedValue: Optional[str] = None
    actualValue: Optional[str] = None
    diffAmount: Optional[float] = None
    detectedAt: Optional[datetime] = None
    detectedBy: Optional[int] = None
    isManual: int = 0
    status: int
    statusLabel: Optional[str] = None
    resolution: Optional[str] = None
    resolvedBy: Optional[int] = None
    resolvedAt: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "ReconDiffOut":
        return cls(
            id=m.id,
            reconKind=m.recon_kind,
            reconId=m.recon_id,
            linkId=m.link_id,
            bizDocType=int(m.biz_doc_type),
            bizDocTypeLabel=BizDocType.LABELS.get(int(m.biz_doc_type)),
            bizDocId=int(m.biz_doc_id),
            bizDocNo=m.biz_doc_no,
            diffType=int(m.diff_type),
            diffTypeLabel=DiffType.LABELS.get(int(m.diff_type)),
            severity=int(m.severity),
            severityLabel=DiffSeverity.LABELS.get(int(m.severity)),
            expectedValue=m.expected_value,
            actualValue=m.actual_value,
            diffAmount=(
                float(m.diff_amount) if m.diff_amount is not None else None
            ),
            detectedAt=m.detected_at,
            detectedBy=m.detected_by,
            isManual=int(m.is_manual or 0),
            status=int(m.status),
            statusLabel=DiffStatus.LABELS.get(int(m.status)),
            resolution=m.resolution,
            resolvedBy=m.resolved_by,
            resolvedAt=m.resolved_at,
        )


class ReconCheckReportOut(BaseModel):
    """一次核对的结论（详情页「一致性核对」区块）"""

    reconId: int
    reconKind: str
    checkedLines: int = 0
    blockingCount: int = 0
    warningCount: int = 0
    dirtyLines: int = 0
    passed: bool = True
    checkedAt: Optional[datetime] = None
    diffs: List[ReconDiffOut] = Field(default_factory=list)


class ReconDiffRaiseRequest(BaseModel):
    """手工登记一条差异（对账工作台）"""

    bizDocId: int = Field(description="关联业务单据 ID")
    diffType: int = Field(
        ge=1, le=8,
        description="1-漏挂 2-重挂 3-资格不符 4-台数不符 "
                    "5-里程不符 6-金额不符 7-扣减不符 8-状态回退",
    )
    bizDocNo: Optional[str] = None
    linkId: Optional[int] = None
    expectedValue: Optional[str] = Field(default=None, max_length=100)
    actualValue: Optional[str] = Field(default=None, max_length=100)
    diffAmount: Optional[float] = None
    severity: Optional[int] = Field(
        default=None, ge=1, le=2, description="1-提示 2-阻塞；不填按类型默认值"
    )


class ReconDiffResolveRequest(BaseModel):
    """处置一条差异"""

    status: int = Field(
        ge=1, le=4,
        description="1-已回灌 2-已协商确认 3-已强制放行 4-已失效",
    )
    resolution: str = Field(min_length=2, max_length=255, description="处置说明")


class ReconForceConfirmRequest(BaseModel):
    """带未决差异强制确认对账单（财务主管）"""

    reason: str = Field(
        min_length=10, max_length=255,
        description="强制确认原因（不少于 10 个字，会写入审计事件）",
    )
