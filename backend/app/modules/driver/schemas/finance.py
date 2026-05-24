"""驾驶员财务相关 Schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DriverFinanceListItem(BaseModel):
    """费用单列表项"""

    id: int
    docNo: str
    docType: int
    isFinal: int = 0
    taskId: int
    taskNo: Optional[str] = None
    payeeName: Optional[str] = None
    plannedAmount: float
    actualAmount: Optional[float] = None
    status: int
    plannedPayTime: Optional[datetime] = None
    actualPayTime: Optional[datetime] = None
    payMethod: Optional[int] = None
    remark: Optional[str] = None


class DriverFinanceItemOut(BaseModel):
    """费用项明细"""

    id: int
    itemType: str
    itemName: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unitPrice: Optional[float] = None
    amount: float


class DriverFinanceDetail(DriverFinanceListItem):
    """费用单详情"""

    items: List[DriverFinanceItemOut] = Field(default_factory=list)
    payVoucherUrl: Optional[str] = None


class FinanceMonthlyAmount(BaseModel):
    month: str
    amount: float


class DriverFinanceSummary(BaseModel):
    """收入汇总"""

    totalIncome: float = 0
    prepaidAmount: float = 0
    supplementAmount: float = 0
    settledAmount: float = 0
    byMonth: List[FinanceMonthlyAmount] = Field(default_factory=list)


class DriverAccountOut(BaseModel):
    """驾驶员结算账户"""

    id: int
    accountType: int
    accountName: str
    accountNo: str
    balance: float = 0
    status: int = 1
