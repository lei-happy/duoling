"""经营核算 Schemas"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AccountingKpiOut(BaseModel):
    """期间 KPI"""

    period: str
    periodLabel: str
    periodStart: date
    periodEnd: date
    taxMode: str = "excl"
    outputTaxRate: float = 9
    confirmedRevenue: float = 0
    realizedRevenue: float = 0
    revenueExclTax: float = 0
    costInclTax: float = 0
    costExclTax: float = 0
    grossProfitInclTax: float = 0
    grossProfitExclTax: float = 0
    grossMarginRate: Optional[float] = None
    noInvoiceCost: float = 0
    missingInvoiceTaxLoss: float = 0
    unallocatedCost: float = 0
    revenueDocCount: int = 0
    costDocCount: int = 0


class DimensionRowOut(BaseModel):
    """维度汇总一行"""

    dimension: str
    dimensionValue: str
    dimensionLabel: Optional[str] = None
    revenue: float = 0
    revenueExclTax: float = 0
    cost: float = 0
    costExclTax: float = 0
    grossProfit: float = 0
    grossMarginRate: Optional[float] = None


class DrillDocOut(BaseModel):
    docKind: str
    docKindLabel: Optional[str] = None
    docId: int
    docNo: Optional[str] = None
    counterparty: Optional[str] = None
    waybillNo: Optional[str] = None
    amount: float = 0
    docAmount: Optional[float] = None
    amountExclTax: Optional[float] = None
    periodEnd: Optional[datetime] = None


class DrillDownOut(BaseModel):
    dimension: str
    dimensionValue: str
    dimensionLabel: Optional[str] = None
    periodLabel: Optional[str] = None
    revenueDocs: List[DrillDocOut] = Field(default_factory=list)
    costDocs: List[DrillDocOut] = Field(default_factory=list)
    revenueTotal: float = 0
    costTotal: float = 0


class InterEntityRowOut(BaseModel):
    waybillId: int
    waybillNo: Optional[str] = None
    taskId: int
    taskNo: Optional[str] = None
    quantity: float = 0
    revenueEntityId: Optional[int] = None
    costEntityId: Optional[int] = None
    revenueAmount: float = 0


class InterEntitySummaryOut(BaseModel):
    enterpriseId: int
    transferOutAmount: float = 0
    transferInAmount: float = 0
    count: int = 0


class InterEntityOut(BaseModel):
    periodLabel: Optional[str] = None
    rows: List[InterEntityRowOut] = Field(default_factory=list)
    byEntity: List[InterEntitySummaryOut] = Field(default_factory=list)
