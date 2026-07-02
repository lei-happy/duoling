"""
财务单据通用基座模型包（租户库）

- ``finance_doc_base.FinanceDocBaseMixin``：所有财务单据共享的通用字段集（mixin，不映射表）。
- ``finance_doc_event.FinanceDocEvent``：财务单据领域内的审计事实流（append-only）。

具体单据表（任务级费用单 / 承运商对账 / 司机工资单等）通过 mixin 复用字段集，
避免每类单据各写一套草稿/审批/支付字段。
"""

from app.modules.client.models.finance.finance_doc_base import (
    FinanceDocBaseMixin,
)
from app.modules.client.models.finance.finance_doc_event import FinanceDocEvent

__all__ = [
    "FinanceDocBaseMixin",
    "FinanceDocEvent",
]
