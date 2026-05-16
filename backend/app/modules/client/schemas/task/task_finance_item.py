"""费用单费用项明细 Schemas"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class TaskFinanceItemIn(BaseModel):
    """费用项入参"""
    itemType: str = Field(min_length=1, max_length=30,
                          description="字典 expense_type 的 key")
    itemName: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unitPrice: Optional[float] = None
    amount: float = Field(gt=0, description="该项金额（>0）")
    sortOrder: int = 0
    remark: Optional[str] = None


class TaskFinanceItemOut(BaseModel):
    id: int
    financeDocId: int
    itemType: str
    itemName: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unitPrice: Optional[float] = None
    amount: float
    sortOrder: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "TaskFinanceItemOut":
        return cls(
            id=m.id,
            financeDocId=m.finance_doc_id,
            itemType=m.item_type,
            itemName=m.item_name,
            quantity=float(m.quantity) if m.quantity is not None else None,
            unit=m.unit,
            unitPrice=float(m.unit_price) if m.unit_price is not None else None,
            amount=float(m.amount),
            sortOrder=m.sort_order,
            remark=m.remark,
            createdAt=m.created_at,
        )
