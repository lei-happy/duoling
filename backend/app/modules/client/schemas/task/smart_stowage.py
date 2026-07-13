"""智能配载 Schemas（专业版 feature: smart_stowage）"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SmartStowageGenerateRequest(BaseModel):
    """一键生成配载方案入参"""

    # ---- 候选筛选 ----
    keyword: Optional[str] = Field(default=None, description="运单号/客户关键字")
    customerId: Optional[int] = Field(default=None, description="客户ID")
    originKeyword: Optional[str] = Field(default=None, description="起点关键字")
    destinationKeyword: Optional[str] = Field(default=None, description="终点关键字")
    modelKeyword: Optional[str] = Field(default=None, description="品牌/车型关键字")
    limit: Optional[int] = Field(default=None, ge=1, le=2000, description="候选拉取上限")

    # ---- 算法参数 ----
    targetSpots: Optional[int] = Field(default=None, ge=1, le=30, description="目标板车车位数")
    minLoadRate: Optional[float] = Field(default=None, ge=0, le=100, description="装载率下限(0-100)")
    maxPlans: Optional[int] = Field(default=None, ge=1, le=100, description="最多产出方案数")
    weights: Optional[Dict[str, float]] = Field(
        default=None, description="打分权重覆盖 {load_rate,aggregation,concentration}"
    )
    occupyOverrides: Optional[Dict[str, float]] = Field(
        default=None, description="占位系数覆盖 {车型关键字: 系数}"
    )


class SmartStowageAdoptRequest(BaseModel):
    """采纳方案入参"""

    remark: Optional[str] = Field(default=None, description="调度备注（默认取方案理由）")


class SmartStowagePlanItemOut(BaseModel):
    id: int
    waybillId: int
    waybillCargoId: int
    quantity: int
    waybillNo: Optional[str] = None
    customerName: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    vin: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    occupyCoefficient: float = 1.0


class SmartStowagePlanOut(BaseModel):
    id: int
    planTaskId: int
    planNo: int
    origin: Optional[str] = None
    destination: Optional[str] = None
    vehicleCount: int = 0
    occupiedSpots: float = 0
    targetSpots: int = 0
    loadRate: float = 0
    customerCount: int = 0
    waybillCount: int = 0
    score: float = 0
    reason: Optional[str] = None
    status: int = 0
    adoptedTaskId: Optional[int] = None
    adoptedAt: Optional[datetime] = None
    items: List[SmartStowagePlanItemOut] = Field(default_factory=list)


class SmartStowageTaskOut(BaseModel):
    id: int
    status: str
    candidateCount: int = 0
    planCount: int = 0
    adoptedCount: int = 0
    errorMessage: Optional[str] = None
    triggeredByName: Optional[str] = None
    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "SmartStowageTaskOut":
        return cls(
            id=m.id,
            status=m.status,
            candidateCount=m.candidate_count or 0,
            planCount=m.plan_count or 0,
            adoptedCount=m.adopted_count or 0,
            errorMessage=m.error_message,
            triggeredByName=m.triggered_by_name,
            startedAt=m.started_at,
            finishedAt=m.finished_at,
            createdAt=m.created_at,
        )
