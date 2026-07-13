"""
智能配载相关模型（专业版 feature: smart_stowage）

- biz_smart_stowage_task        方案生成任务（认领模式，供异步/同步共用）
- biz_smart_stowage_plan        推荐配载方案
- biz_smart_stowage_plan_item   方案明细（商品车挂接候选）
"""

from app.modules.client.models.task.smart_stowage.stowage_plan_task import (
    SmartStowagePlanTask,
)
from app.modules.client.models.task.smart_stowage.stowage_plan import (
    PLAN_STATUS_ADOPTED,
    PLAN_STATUS_IGNORED,
    PLAN_STATUS_PENDING,
    SmartStowagePlan,
)
from app.modules.client.models.task.smart_stowage.stowage_plan_item import (
    SmartStowagePlanItem,
)

__all__ = [
    "SmartStowagePlanTask",
    "SmartStowagePlan",
    "SmartStowagePlanItem",
    "PLAN_STATUS_PENDING",
    "PLAN_STATUS_ADOPTED",
    "PLAN_STATUS_IGNORED",
]
