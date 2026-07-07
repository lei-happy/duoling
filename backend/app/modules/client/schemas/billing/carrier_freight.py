"""
承运商运费计算 Schemas（试算 / 结果查询）
"""

from typing import Optional
from decimal import Decimal
from datetime import date
from pydantic import BaseModel


class CarrierFreightPreviewVehicle(BaseModel):
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int = 0


class CarrierFreightPreviewRequest(BaseModel):
    """试算请求：既可传 taskId 直接用任务事实数据，也可传散字段做纯试算。"""

    taskId: Optional[int] = None
    carrierId: Optional[int] = None
    originRegionId: Optional[int] = None
    destinationRegionId: Optional[int] = None
    totalQuantity: Optional[int] = None
    vehicles: Optional[list[CarrierFreightPreviewVehicle]] = None
    transportDate: Optional[date] = None


class CarrierFreightItemOut(BaseModel):
    brandId: Optional[int] = None
    seriesId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int = 0
    matchedContractId: Optional[int] = None
    matchedRuleId: Optional[int] = None
    matchedRuleVersion: Optional[int] = None
    direction: Optional[str] = None
    modelMatchType: Optional[str] = None
    originMatchLevel: Optional[str] = None
    destinationMatchLevel: Optional[str] = None
    unitPrice: Optional[float] = None
    billingMode: Optional[int] = None
    distanceKm: Optional[float] = None
    amount: float = 0
    matchScore: Optional[int] = None
    calcStatus: str
    errorType: Optional[str] = None
    errorMessage: Optional[str] = None
    matchTrace: Optional[dict] = None


class CarrierFreightResultOut(BaseModel):
    taskId: int
    totalAmount: float
    calcStatus: str
    carrierId: Optional[int] = None
    carrierName: Optional[str] = None
    matchedContractId: Optional[int] = None
    errorMessage: Optional[str] = None
    items: list[CarrierFreightItemOut] = []
