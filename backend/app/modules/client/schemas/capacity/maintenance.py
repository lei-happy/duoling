"""车辆资产 - 维修保养 Schemas"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkOrderLineIn(BaseModel):
    lineType: str = Field(..., description="labor/part/other")
    partId: Optional[int] = None
    title: str
    qty: Decimal = Decimal("1")
    unitPrice: Optional[Decimal] = None
    laborHours: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    sortOrder: int = 0


class WorkOrderLineOut(BaseModel):
    id: int
    workOrderId: int
    lineType: str
    partId: Optional[int] = None
    title: str
    qty: Decimal
    unitPrice: Optional[Decimal] = None
    laborHours: Optional[Decimal] = None
    amount: Decimal
    sortOrder: int


class WorkOrderCreate(BaseModel):
    vehicleId: int
    orderType: str = Field(..., description="repair/maintenance")
    title: str
    planId: Optional[int] = None
    description: Optional[str] = None
    odometer: Optional[int] = None
    faultCategory: Optional[str] = None
    workshopId: Optional[int] = None
    workshop: Optional[str] = None
    expectFinishDate: Optional[date] = None
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None
    lines: Optional[List[WorkOrderLineIn]] = None


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    odometer: Optional[int] = None
    faultCategory: Optional[str] = None
    workshopId: Optional[int] = None
    workshop: Optional[str] = None
    expectFinishDate: Optional[date] = None
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None
    lines: Optional[List[WorkOrderLineIn]] = None


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
    faultCategory: Optional[str] = None
    workshopId: Optional[int] = None
    workshop: Optional[str] = None
    expectFinishDate: Optional[date] = None
    laborAmount: Optional[Decimal] = None
    partsAmount: Optional[Decimal] = None
    costAmount: Optional[Decimal] = None
    costRemark: Optional[str] = None
    status: str
    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    capacityId: Optional[int] = None
    remark: Optional[str] = None
    lines: Optional[List[WorkOrderLineOut]] = None
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


# ---------- 工单做厚：备件 / 维修厂 / 库存 ----------


class PartCreate(BaseModel):
    partCode: str
    partName: str
    category: Optional[str] = None
    unit: str = "个"
    refPrice: Optional[Decimal] = None
    safetyStock: int = 0
    remark: Optional[str] = None


class PartUpdate(BaseModel):
    partName: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    refPrice: Optional[Decimal] = None
    safetyStock: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class PartOut(BaseModel):
    id: int
    partCode: str
    partName: str
    category: Optional[str] = None
    unit: str
    refPrice: Optional[Decimal] = None
    safetyStock: int
    qtyOnHand: Decimal
    status: int
    lowStock: bool = False
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class StockInboundBody(BaseModel):
    qty: Decimal = Field(..., gt=0)
    unitCost: Optional[Decimal] = None
    remark: Optional[str] = None


class StockAdjustBody(BaseModel):
    qtyDelta: Decimal = Field(..., description="正数盘盈、负数盘亏")
    remark: Optional[str] = None


class StockTxnOut(BaseModel):
    id: int
    partId: int
    partCode: str
    partName: str
    txnType: str
    qty: Decimal
    unitCost: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    refType: Optional[str] = None
    refId: Optional[int] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None


class WorkshopCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    enabled: int = 1
    remark: Optional[str] = None


class WorkshopUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    enabled: Optional[int] = None
    remark: Optional[str] = None


class WorkshopOut(BaseModel):
    id: int
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    enabled: int
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
