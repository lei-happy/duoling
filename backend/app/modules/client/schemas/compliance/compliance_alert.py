"""
证照监控 - 预警 Schemas
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# 主体类型 / 证照类型的中文展示映射（供前端兜底）
SUBJECT_TYPE_LABELS = {
    "driver": "自有驾驶员",
    "vehicle": "自有车辆",
    "social_driver": "社会运力-司机",
    "social_vehicle": "社会运力-车辆",
    "carrier_driver": "承运商运力-司机",
    "carrier_vehicle": "承运商运力-车辆",
}
DOC_TYPE_LABELS = {
    "driver_license": "驾驶证",
    "qualification": "从业资格证",
    "insurance": "保险",
    "inspection": "年检",
    "transport_license": "道路运输证",
}


class ComplianceAlertOut(BaseModel):
    """预警响应"""

    id: int
    subjectType: str
    subjectTypeLabel: Optional[str] = None
    subjectId: int
    subjectName: str
    subjectRef: Optional[str] = None
    docType: str
    docTypeLabel: Optional[str] = None
    docNo: Optional[str] = None
    expireDate: Optional[date] = None
    daysLeft: int
    level: str
    status: str
    dismissedUserId: Optional[int] = None
    dismissedAt: Optional[datetime] = None
    firstAlertedAt: Optional[datetime] = None
    lastScanAt: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "ComplianceAlertOut":
        return cls(
            id=m.id,
            subjectType=m.subject_type,
            subjectTypeLabel=SUBJECT_TYPE_LABELS.get(m.subject_type),
            subjectId=m.subject_id,
            subjectName=m.subject_name,
            subjectRef=m.subject_ref,
            docType=m.doc_type,
            docTypeLabel=DOC_TYPE_LABELS.get(m.doc_type),
            docNo=m.doc_no,
            expireDate=m.expire_date,
            daysLeft=m.days_left,
            level=m.level,
            status=m.status,
            dismissedUserId=m.dismissed_user_id,
            dismissedAt=m.dismissed_at,
            firstAlertedAt=m.first_alerted_at,
            lastScanAt=m.last_scan_at,
        )


class ComplianceAlertSummary(BaseModel):
    """合规看板汇总"""

    total: int = 0
    expired: int = 0
    critical: int = 0
    warning: int = 0
    # 按主体类型分组的待处理数量
    bySubjectType: dict = {}
    # 按证照类型分组的待处理数量
    byDocType: dict = {}


class ComplianceAlertDismiss(BaseModel):
    """忽略预警"""

    remark: Optional[str] = None
