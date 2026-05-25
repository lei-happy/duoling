"""
社会运力池 Schema - 审核与状态流水
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class SocialCapacityAuditOut(BaseModel):
    """审核 / 状态流水响应"""

    id: int
    socialCapacityId: int
    action: int
    beforeStatus: Optional[int] = None
    afterStatus: Optional[int] = None
    operatorUserId: int
    operatorName: Optional[str] = None
    remark: Optional[str] = None
    attachment: Optional[Any] = None
    approvalFlowInstId: Optional[int] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "SocialCapacityAuditOut":
        return cls(
            id=m.id,
            socialCapacityId=m.social_capacity_id,
            action=m.action,
            beforeStatus=m.before_status,
            afterStatus=m.after_status,
            operatorUserId=m.operator_user_id,
            operatorName=m.operator_name,
            remark=m.remark,
            attachment=m.attachment,
            approvalFlowInstId=m.approval_flow_inst_id,
            createdAt=m.created_at,
        )
