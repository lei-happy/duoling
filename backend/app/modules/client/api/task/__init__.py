"""运输任务单 + 任务单财务费用单 + 智能配载 API"""

from app.modules.client.api.task.task import router as task_router
from app.modules.client.api.task.task_alert import (
    alert_router as task_alert_router,
    alert_rule_router as task_alert_rule_router,
)
from app.modules.client.api.task.task_finance import router as task_finance_router
from app.modules.client.api.task.smart_stowage import router as smart_stowage_router

__all__ = [
    "task_router",
    "task_alert_router",
    "task_alert_rule_router",
    "task_finance_router",
    "smart_stowage_router",
]
