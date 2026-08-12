"""
任务预警子域

- ``catalog``  规则类型目录与内置默认阈值（阈值三层模型第 1 层）
- ``context``  求值上下文的批量装配（客户要求时间、车型、里程、运力状态…）
- ``matcher``  维度覆盖规则的特异度匹配（第 2、3 层）
- ``engine``   判定与落库，维护预警生命周期
- ``tracking`` 状态变更后的即时重算（会话提交前钩子）

导入本包即完成即时重算通道的注册，业务代码无需感知。
"""

from app.modules.client.services.task.alert.catalog import (
    ALERT_RULE_CATALOG,
    CATALOG_BY_CODE,
    catalog_payload,
)
from app.modules.client.services.task.alert.engine import TaskAlertEngine
from app.modules.client.services.task.alert.tracking import (  # noqa: F401
    sync_pending_task_alerts,
)

__all__ = [
    "ALERT_RULE_CATALOG",
    "CATALOG_BY_CODE",
    "catalog_payload",
    "TaskAlertEngine",
    "sync_pending_task_alerts",
]
