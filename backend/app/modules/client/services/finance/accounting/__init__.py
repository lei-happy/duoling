"""经营核算 service 包（文档 13）

- ``profit_accounting_service``：财务确认口径的收入 / 成本 / 毛利聚合；
- ``cost_allocator``：任务成本按台数摊到运单的纯函数工具；
- ``accounting_constants``：纳入状态集、默认税率、维度等口径常量。
"""

from app.modules.client.services.finance.accounting.cost_allocator import (
    allocate_task_cost_to_waybills,
    split_doc_amount_by_task,
)
from app.modules.client.services.finance.accounting.profit_accounting_service import (
    ProfitAccountingService,
)

__all__ = [
    "ProfitAccountingService",
    "allocate_task_cost_to_waybills",
    "split_doc_amount_by_task",
]
