"""
任务成本计算 Schemas（试算 / 结果查询）
"""

from typing import Optional
from decimal import Decimal
from datetime import date
from pydantic import BaseModel


class TaskCostPreviewVehicle(BaseModel):
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int = 0


class TaskCostPreviewRequest(BaseModel):
    """试算请求：既可传 taskId 直接用任务事实数据，也可传散字段做纯试算。"""

    taskId: Optional[int] = None
    carrierType: Optional[int] = None
    capacityId: Optional[int] = None
    carrierId: Optional[int] = None
    driverId: Optional[int] = None
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    totalQuantity: Optional[int] = None
    vehicles: Optional[list[TaskCostPreviewVehicle]] = None
    distanceKm: Optional[Decimal] = None
    transportDate: Optional[date] = None


class TaskCostItemOut(BaseModel):
    feeType: str
    feeName: Optional[str] = None
    direction: int
    payeeType: Optional[int] = None
    pricingMethod: Optional[str] = None
    unitPrice: Optional[float] = None
    quantity: Optional[float] = None
    distanceKm: Optional[float] = None
    amount: float
    matchedPolicyId: Optional[int] = None
    matchedRuleId: Optional[int] = None
    matchedRuleVersion: Optional[int] = None
    matchScore: Optional[int] = None
    calcStatus: str
    errorType: Optional[str] = None
    errorMessage: Optional[str] = None
    matchTrace: Optional[dict] = None


class TaskCostResultOut(BaseModel):
    taskId: int
    totalCostAmount: float
    totalAdditionAmount: float
    totalDeductionAmount: float
    calcStatus: str
    carrierType: Optional[int] = None
    payeeType: Optional[int] = None
    payeeId: Optional[int] = None
    payeeName: Optional[str] = None
    errorMessage: Optional[str] = None
    items: list[TaskCostItemOut] = []
