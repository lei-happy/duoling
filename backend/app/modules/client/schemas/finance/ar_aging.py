"""应收账龄 Schemas

账龄是聚合视图而非单据，``AgingService`` 直接产出 camelCase 字典；这里的模型只用
来固定对外契约与生成接口文档，故统一 ``extra="ignore"``，服务层多给的中间字段不
会漏到前端。
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

_IGNORE_EXTRA = {"extra": "ignore"}


class AgingBucketCell(BaseModel):
    """一个账龄桶的金额与笔数"""

    bucket: int
    label: str
    amount: float = 0
    count: int = 0

    model_config = _IGNORE_EXTRA


class AgingCustomerRow(BaseModel):
    """客户维度汇总行（催收主视图）"""

    customerId: int
    customerName: Optional[str] = None
    enterpriseId: Optional[int] = None
    creditStatus: int = 1
    creditStatusLabel: Optional[str] = None
    creditLimit: Optional[float] = None
    unpaidAmount: float = 0
    overdueAmount: float = 0
    maxOverdueDays: int = 0
    settleCount: int = 0
    exceeded: bool = False
    exceededAmount: float = 0
    bucketSummary: List[AgingBucketCell] = Field(default_factory=list)

    model_config = _IGNORE_EXTRA


class AgingSettleDetail(BaseModel):
    """客户展开后的结算单明细行"""

    settleId: int
    docNo: str
    customerId: int
    customerName: Optional[str] = None
    enterpriseId: Optional[int] = None
    status: int
    plannedAmount: float = 0
    receivedAmount: float = 0
    unpaidAmount: float = 0
    dueDate: Optional[date] = None
    dueDateOverridden: bool = False
    overdueDays: int = 0
    bucket: int = 0
    bucketLabel: Optional[str] = None
    periodStart: Optional[date] = None
    periodEnd: Optional[date] = None

    model_config = _IGNORE_EXTRA


class CustomerCreditBrief(AgingCustomerRow):
    """单客户预警摘要（业务侧页面同步调用）

    ``alertLevel`` 0-无 1-提醒 2-警示 3-高危；``alertMessage`` 可直接展示，
    无预警时为空。任何等级都**不阻断**业务操作。
    """

    alertLevel: int = 0
    alertLevelLabel: Optional[str] = None
    alertMessage: Optional[str] = None
    buckets: List[int] = Field(default_factory=list)
    bucketLabels: List[str] = Field(default_factory=list)

    model_config = _IGNORE_EXTRA
