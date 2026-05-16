"""
任务单费用单费用项明细（租户库）

每张费用单挂多条费用项。item_type 取自数据字典 expense_type。
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, Index, Integer, Numeric, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskFinanceItem(TenantModelBase):
    """费用单费用项明细"""

    __tablename__ = "biz_task_finance_item"
    __table_args__ = (
        Index("idx_tfi_doc_id", "finance_doc_id"),
        {"comment": "任务单费用单费用项明细"},
    )
    __table_tier__ = "business"

    finance_doc_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task_finance_doc.id"
    )
    item_type: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="字典 expense_type 的 key（oil/toll/loading/parking/meal/repair/other）",
    )
    item_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="字典 label（冗余）"
    )
    quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="数量（如 50 升）"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="单位（升/公里/趟/次）"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="单价"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="该项金额（>0）"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="排序"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
