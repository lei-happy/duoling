"""社会运力池 Schema 聚合"""

from app.modules.client.schemas.capacity.social_capacity.social_capacity import (
    SocialCapacityVehicleInfo,
    SocialCapacityDriverInfo,
    SocialCapacityCreate,
    SocialCapacityUpdate,
    SocialCapacityStatusUpdate,
    SocialCapacityApproveAction,
    SocialCapacityRejectAction,
    SocialCapacitySubmitAction,
    SocialCapacityAccountBrief,
    SocialCapacityAuditBrief,
    SocialCapacityListItem,
    SocialCapacityDetail,
    SocialCapacitySelectItem,
)
from app.modules.client.schemas.capacity.social_capacity.social_capacity_account import (
    SocialCapacityAccountCreate,
    SocialCapacityAccountUpdate,
    SocialCapacityAccountOut,
)
from app.modules.client.schemas.capacity.social_capacity.social_capacity_audit import (
    SocialCapacityAuditOut,
)

__all__ = [
    "SocialCapacityVehicleInfo",
    "SocialCapacityDriverInfo",
    "SocialCapacityCreate",
    "SocialCapacityUpdate",
    "SocialCapacityStatusUpdate",
    "SocialCapacityApproveAction",
    "SocialCapacityRejectAction",
    "SocialCapacitySubmitAction",
    "SocialCapacityAccountBrief",
    "SocialCapacityAuditBrief",
    "SocialCapacityListItem",
    "SocialCapacityDetail",
    "SocialCapacitySelectItem",
    "SocialCapacityAccountCreate",
    "SocialCapacityAccountUpdate",
    "SocialCapacityAccountOut",
    "SocialCapacityAuditOut",
]
