"""车辆资产 - 维修保养 Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class WorkOrderCreate(BaseModel):
    vehicleId: int
    orderType: str = Field(..., description="repair/maintenance")
    title: str
    planId: Optional[int] = None
    description: Optional[str] = None
    odometer: Optional[int] = None
    workshop: Optional[str] = None
    expectFinishDate: Optional[date] = None
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    odometer: Optional[int] = None
    workshop: Optional[str] = None
    expectFinishDate: Optional[date] = None
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None


class WorkOrderCompleteBody(BaseModel):
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    odometer: Optional[int] = None
    remark: Optional[str] = None


class WorkOrderOut(BaseModel):
    id: int
    workOrderNo: str
    vehicleId: int
    plateNumber: str
    orderType: str
    planId: Optional[int] = None
    title: str
    description: Optional[str] = None
    odometer: Optional[int] = None
    workshop: Optional[str] = None
    expectFinishDate: Optional[date] = None
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    status: str
    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    capacityId: Optional[int] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class MaintainPlanCreate(BaseModel):
    vehicleId: int
    name: str
    cycleType: str
    intervalDays: Optional[int] = None
    intervalMileage: Optional[int] = None
    lastMaintainDate: Optional[date] = None
    lastMaintainMileage: Optional[int] = None
    remindDays: int = 7
    enabled: int = 1


class MaintainPlanUpdate(BaseModel):
    name: Optional[str] = None
    cycleType: Optional[str] = None
    intervalDays: Optional[int] = None
    intervalMileage: Optional[int] = None
    lastMaintainDate: Optional[date] = None
    lastMaintainMileage: Optional[int] = None
    remindDays: Optional[int] = None
    enabled: Optional[int] = None


class MaintainPlanOut(BaseModel):
    id: int
    vehicleId: int
    plateNumber: str
    name: str
    cycleType: str
    intervalDays: Optional[int] = None
    intervalMileage: Optional[int] = None
    lastMaintainDate: Optional[date] = None
    lastMaintainMileage: Optional[int] = None
    nextMaintainDate: Optional[date] = None
    nextMaintainMileage: Optional[int] = None
    remindDays: int
    enabled: int
    dueLevel: Optional[str] = None  # overdue / due_soon / ok
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# ---------- 二期：续期台账 / 资产卡片 / 成本 ----------


class RenewalCreate(BaseModel):
    vehicleId: int
    renewalType: str = Field(..., description="insurance/inspection")
    effectiveDate: date
    expireDate: date
    amount: Optional[Decimal] = None
    policyNo: Optional[str] = None
    attachmentUrl: Optional[str] = None
    remark: Optional[str] = None
    effectNow: bool = Field(
        True, description="创建后立即生效并回写到期日"
    )


class RenewalUpdate(BaseModel):
    effectiveDate: Optional[date] = None
    expireDate: Optional[date] = None
    amount: Optional[Decimal] = None
    policyNo: Optional[str] = None
    attachmentUrl: Optional[str] = None
    remark: Optional[str] = None


class RenewalOut(BaseModel):
    id: int
    vehicleId: int
    plateNumber: str
    renewalType: str
    effectiveDate: date
    expireDate: date
    amount: Optional[Decimal] = None
    policyNo: Optional[str] = None
    attachmentUrl: Optional[str] = None
    status: str
    effectiveAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class AssetCardUpdate(BaseModel):
    purchaseDate: Optional[date] = None
    originalValue: Optional[Decimal] = None
    residualValue: Optional[Decimal] = None
    depreciableMonths: Optional[int] = None
    depreciationMethod: Optional[str] = None
    depreciationStartDate: Optional[date] = None


class AssetCardOut(BaseModel):
    vehicleId: int
    plateNumber: str
    purchaseDate: Optional[date] = None
    originalValue: Optional[Decimal] = None
    residualValue: Optional[Decimal] = None
    depreciableMonths: Optional[int] = None
    depreciationMethod: Optional[str] = None
    depreciationStartDate: Optional[date] = None
    insuranceExpire: Optional[date] = None
    inspectionExpire: Optional[date] = None
    monthlyDepreciation: Optional[Decimal] = None
    accumulatedDepreciation: Optional[Decimal] = None
    netValue: Optional[Decimal] = None
