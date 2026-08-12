"""任务预警与预警规则的出入参 Schema"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator

from app.modules.client.models.task.task_alert import (
    ALERT_LEVEL_LABELS,
    ALERT_STATUS_LABELS,
)
from app.modules.client.models.task.task_alert_rule import (
    clocks_from_time_basis,
    time_basis_from_clocks,
)
from app.modules.client.services.task.alert.catalog import (
    CATALOG_BY_CODE,
    STAGE_LABELS,
)


class TaskAlertOut(BaseModel):
    """预警实例"""

    id: int
    taskId: int
    taskNo: Optional[str] = None
    stage: int
    stageLabel: Optional[str] = None
    ruleCode: str
    ruleName: Optional[str] = None
    ruleId: Optional[int] = None
    level: int
    levelLabel: Optional[str] = None
    status: int
    statusLabel: Optional[str] = None
    dueAt: Optional[datetime] = None
    overdueMinutes: int = 0
    triggeredAt: Optional[datetime] = None
    escalatedAt: Optional[datetime] = None
    handlerName: Optional[str] = None
    claimedAt: Optional[datetime] = None
    resolvedAt: Optional[datetime] = None
    resolveType: Optional[str] = None
    resolveRemark: Optional[str] = None
    snapshot: Optional[Any] = None

    @classmethod
    def from_model(cls, m) -> "TaskAlertOut":
        rule_def = CATALOG_BY_CODE.get(m.rule_code)
        return cls(
            id=m.id,
            taskId=m.task_id,
            taskNo=m.task_no,
            stage=m.stage,
            stageLabel=STAGE_LABELS.get(int(m.stage)),
            ruleCode=m.rule_code,
            ruleName=rule_def.name if rule_def else m.rule_code,
            ruleId=m.rule_id,
            level=m.level,
            levelLabel=ALERT_LEVEL_LABELS.get(int(m.level)),
            status=m.status,
            statusLabel=ALERT_STATUS_LABELS.get(int(m.status)),
            dueAt=m.due_at,
            overdueMinutes=int(m.overdue_minutes or 0),
            triggeredAt=m.triggered_at,
            escalatedAt=m.escalated_at,
            handlerName=m.handler_name,
            claimedAt=m.claimed_at,
            resolvedAt=m.resolved_at,
            resolveType=m.resolve_type,
            resolveRemark=m.resolve_remark,
            snapshot=m.snapshot_json,
        )


class TaskAlertResolveRequest(BaseModel):
    remark: Optional[str] = Field(default=None, max_length=255)


class TaskAlertDismissRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=255)


class TaskAlertBatchDismissRequest(BaseModel):
    ids: List[int] = Field(default_factory=list)
    taskIds: List[int] = Field(default_factory=list)
    reason: str = Field(..., min_length=1, max_length=255)


# ============================================================
# 预警规则
# ============================================================

class TaskAlertRuleBase(BaseModel):
    ruleCode: str = Field(..., max_length=32)
    ruleName: Optional[str] = Field(default=None, max_length=100)
    stage: Optional[int] = None

    customerId: Optional[int] = None
    customerType: Optional[int] = None
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    distanceMin: Optional[float] = None
    distanceMax: Optional[float] = None
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    carrierType: Optional[int] = None

    timeBasis: int = 2
    planEnabled: Optional[bool] = None
    requiredEnabled: Optional[bool] = None
    anchorOffsetMinutes: Optional[int] = Field(default=None, ge=0)
    warnAheadMinutes: Optional[int] = Field(default=None, ge=0)
    criticalAfterMinutes: Optional[int] = Field(default=None, ge=0)
    warnAheadRequiredMinutes: Optional[int] = Field(default=None, ge=0)
    criticalAfterRequiredMinutes: Optional[int] = Field(default=None, ge=0)
    stagnantHours: Optional[int] = Field(default=None, ge=1)

    priority: int = 0
    status: int = 1
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    remark: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _sync_clocks(self):
        if self.planEnabled is None and self.requiredEnabled is None:
            plan, req = clocks_from_time_basis(self.timeBasis)
            self.planEnabled = bool(plan)
            self.requiredEnabled = bool(req)
        else:
            plan = True if self.planEnabled is None else bool(self.planEnabled)
            req = True if self.requiredEnabled is None else bool(self.requiredEnabled)
            self.planEnabled = plan
            self.requiredEnabled = req
            self.timeBasis = time_basis_from_clocks(int(plan), int(req))
        return self


class TaskAlertRuleCreate(TaskAlertRuleBase):
    pass


class TaskAlertRuleUpdate(TaskAlertRuleBase):
    pass


class TaskAlertRuleOut(TaskAlertRuleBase):
    id: int
    ruleVersion: int = 1
    isDefault: bool = Field(
        default=False, description="是否为租户默认阈值（未限定任何维度）"
    )
    scopeSummary: Optional[str] = Field(
        default=None, description="适用范围的可读摘要，供列表直接展示"
    )
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m, *, scope_summary: Optional[str] = None) -> "TaskAlertRuleOut":
        rule_def = CATALOG_BY_CODE.get(m.rule_code)
        return cls(
            id=m.id,
            ruleCode=m.rule_code,
            ruleName=m.rule_name or (rule_def.name if rule_def else None),
            stage=m.stage,
            customerId=m.customer_id,
            customerType=m.customer_type,
            originRegionId=m.origin_region_id,
            destinationRegionId=m.destination_region_id,
            distanceMin=float(m.distance_min) if m.distance_min is not None else None,
            distanceMax=float(m.distance_max) if m.distance_max is not None else None,
            brandId=m.brand_id,
            seriesId=m.series_id,
            carrierType=m.carrier_type,
            timeBasis=m.time_basis,
            planEnabled=(
                bool(int(m.plan_enabled))
                if getattr(m, "plan_enabled", None) is not None
                else True
            ),
            requiredEnabled=(
                bool(int(m.required_enabled))
                if getattr(m, "required_enabled", None) is not None
                else True
            ),
            anchorOffsetMinutes=m.anchor_offset_minutes,
            warnAheadMinutes=m.warn_ahead_minutes,
            criticalAfterMinutes=m.critical_after_minutes,
            warnAheadRequiredMinutes=getattr(
                m, "warn_ahead_required_minutes", None
            ),
            criticalAfterRequiredMinutes=getattr(
                m, "critical_after_required_minutes", None
            ),
            stagnantHours=m.stagnant_hours,
            priority=m.priority,
            status=m.status,
            effectiveDate=m.effective_date,
            expiryDate=m.expiry_date,
            remark=m.remark,
            ruleVersion=m.rule_version,
            isDefault=not m.has_scope(),
            scopeSummary=scope_summary,
            createdAt=m.created_at,
        )


class TaskAlertRuleConflictOut(BaseModel):
    hasConflict: bool = False
    conflicts: List[TaskAlertRuleOut] = Field(default_factory=list)
    message: Optional[str] = None
