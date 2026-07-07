"""
成本政策 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class CostPolicyCreate(BaseModel):
    policyNo: str
    policyName: str
    scopeType: int = 0
    scopeId: Optional[int] = None
    carrierType: Optional[int] = None
    effectiveDate: date
    expiryDate: Optional[date] = None
    priority: Optional[int] = 0
    remark: Optional[str] = None


class CostPolicyUpdate(BaseModel):
    policyName: Optional[str] = None
    scopeType: Optional[int] = None
    scopeId: Optional[int] = None
    carrierType: Optional[int] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[int] = None
    priority: Optional[int] = None
    remark: Optional[str] = None


class CostPolicyOut(BaseModel):
    id: int
    policyNo: str
    policyName: str
    scopeType: int
    scopeId: Optional[int] = None
    carrierType: Optional[int] = None
    effectiveDate: date
    expiryDate: Optional[date] = None
    status: int
    priority: int
    versionNo: int
    remark: Optional[str] = None
    createdAt: datetime
    ruleCount: int = 0
    activeRuleCount: int = 0

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "CostPolicyOut":
        return cls(
            id=m.id,
            policyNo=m.policy_no,
            policyName=m.policy_name,
            scopeType=m.scope_type,
            scopeId=m.scope_id,
            carrierType=m.carrier_type,
            effectiveDate=m.effective_date,
            expiryDate=m.expiry_date,
            status=m.status,
            priority=m.priority,
            versionNo=m.version_no,
            remark=m.remark,
            createdAt=m.created_at,
        )
