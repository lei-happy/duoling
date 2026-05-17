"""任务单主表 Schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.modules.client.schemas.task.task_segment import (
    TaskSegmentIn, TaskSegmentOut,
)
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemIn, TaskWaybillItemOut,
)


class TaskCarrierInfo(BaseModel):
    """承运方信息（可被嵌入 Create / Update / Assign）"""
    carrierType: int = Field(ge=1, le=3,
                             description="1-自有车 2-承运商 3-社会运力")
    capacityId: Optional[int] = None
    carrierId: Optional[int] = None
    socialDriverId: Optional[int] = None
    mainDriverName: Optional[str] = None
    mainDriverPhone: Optional[str] = None
    mainDriverIdCard: Optional[str] = None
    plateNumber: Optional[str] = None
    trailerPlateNumber: Optional[str] = None
    carrierName: Optional[str] = None
    carrierShortName: Optional[str] = None

    @model_validator(mode="after")
    def _check_required(self):
        # 自有车与承运商需要至少有对应的 ID 或快照
        if self.carrierType == 1:
            if not (self.capacityId or (self.mainDriverName and self.plateNumber)):
                raise ValueError("自有车任务必须选择运力或填写主驾+车牌")
        elif self.carrierType == 2:
            if not (self.carrierId or self.carrierName):
                raise ValueError("承运商任务必须选择承运商或填写承运商名称")
        elif self.carrierType == 3:
            if not (self.mainDriverName and self.mainDriverPhone and self.plateNumber):
                raise ValueError("社会运力必须填写司机姓名/电话/车牌")
        return self


class TaskCreate(BaseModel):
    """创建任务单"""
    taskNo: Optional[str] = None
    taskName: Optional[str] = None
    source: int = 1
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    carrierCostType: Optional[int] = None
    carrierCostAmount: Optional[float] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None

    # 承运方（可选，未填则保存为"待派车"）
    carrier: Optional[TaskCarrierInfo] = None

    # 至少 1 段
    segments: List[TaskSegmentIn] = Field(default_factory=list, min_length=1)
    # 至少 1 条挂接
    waybillItems: List[TaskWaybillItemIn] = Field(
        default_factory=list, min_length=1
    )

    @model_validator(mode="after")
    def _check_segments(self):
        nos = [s.segmentNo for s in self.segments]
        if len(set(nos)) != len(nos):
            raise ValueError("段序号不允许重复")
        if sorted(nos) != list(range(1, len(nos) + 1)):
            raise ValueError("段序号必须从 1 开始连续")
        return self


class TaskUpdate(BaseModel):
    """更新任务单（status=0/1 时允许）"""
    taskName: Optional[str] = None
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    carrierCostType: Optional[int] = None
    carrierCostAmount: Optional[float] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None
    carrier: Optional[TaskCarrierInfo] = None
    segments: Optional[List[TaskSegmentIn]] = None
    waybillItems: Optional[List[TaskWaybillItemIn]] = None


class TaskStatusUpdate(BaseModel):
    status: int = Field(ge=0, le=9)
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    remark: Optional[str] = None


class TaskAssignCarrierRequest(BaseModel):
    """派车（设置承运方）"""
    carrier: TaskCarrierInfo
    carrierCostType: Optional[int] = None
    carrierCostAmount: Optional[float] = None
    costRemark: Optional[str] = None


class TaskCancelRequest(BaseModel):
    reason: Optional[str] = None


class TaskBatchStatusRequest(BaseModel):
    """批量推进任务单状态"""
    ids: List[int] = Field(min_length=1)
    status: int = Field(ge=0, le=9)
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    remark: Optional[str] = None


class TaskListItemOut(BaseModel):
    """列表行（不含 segments / items 详情）"""
    id: int
    taskNo: str
    taskName: Optional[str] = None
    carrierType: int
    capacityId: Optional[int] = None
    carrierId: Optional[int] = None
    mainDriverName: Optional[str] = None
    mainDriverPhone: Optional[str] = None
    plateNumber: Optional[str] = None
    carrierName: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    segmentCount: int
    totalQuantity: int
    waybillCount: int
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    carrierCostAmount: Optional[float] = None
    prepaidAmount: float
    supplementAmount: float
    settledAmount: float
    financeDocCount: int
    status: int
    dispatcherName: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "TaskListItemOut":
        return cls(
            id=m.id,
            taskNo=m.task_no,
            taskName=m.task_name,
            carrierType=m.carrier_type,
            capacityId=m.capacity_id,
            carrierId=m.carrier_id,
            mainDriverName=m.main_driver_name,
            mainDriverPhone=m.main_driver_phone,
            plateNumber=m.plate_number,
            carrierName=m.carrier_name,
            origin=m.origin,
            destination=m.destination,
            segmentCount=m.segment_count,
            totalQuantity=m.total_quantity,
            waybillCount=m.waybill_count,
            plannedLoadTime=m.planned_load_time,
            plannedArriveTime=m.planned_arrive_time,
            actualLoadTime=m.actual_load_time,
            actualArriveTime=m.actual_arrive_time,
            carrierCostAmount=(
                float(m.carrier_cost_amount)
                if m.carrier_cost_amount is not None else None
            ),
            prepaidAmount=float(m.prepaid_amount or 0),
            supplementAmount=float(m.supplement_amount or 0),
            settledAmount=float(m.settled_amount or 0),
            financeDocCount=m.finance_doc_count,
            status=m.status,
            dispatcherName=m.dispatcher_name,
            createdAt=m.created_at,
        )


class TaskOut(BaseModel):
    """任务单详情（聚合 segments / waybillItems）"""
    id: int
    taskNo: str
    taskName: Optional[str] = None
    source: int
    carrierType: int
    capacityId: Optional[int] = None
    carrierId: Optional[int] = None
    socialDriverId: Optional[int] = None
    mainDriverName: Optional[str] = None
    mainDriverPhone: Optional[str] = None
    mainDriverIdCard: Optional[str] = None
    plateNumber: Optional[str] = None
    trailerPlateNumber: Optional[str] = None
    carrierName: Optional[str] = None
    carrierShortName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    segmentCount: int
    totalQuantity: int
    waybillCount: int
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    carrierCostAmount: Optional[float] = None
    carrierCostType: Optional[int] = None
    costRemark: Optional[str] = None
    prepaidAmount: float
    supplementAmount: float
    settledAmount: float
    financeDocCount: int
    status: int
    dispatcherId: Optional[int] = None
    dispatcherName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    segments: List[TaskSegmentOut] = Field(default_factory=list)
    waybillItems: List[TaskWaybillItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        m,
        segments: Optional[list] = None,
        waybill_items: Optional[list] = None,
    ) -> "TaskOut":
        return cls(
            id=m.id,
            taskNo=m.task_no,
            taskName=m.task_name,
            source=m.source,
            carrierType=m.carrier_type,
            capacityId=m.capacity_id,
            carrierId=m.carrier_id,
            socialDriverId=m.social_driver_id,
            mainDriverName=m.main_driver_name,
            mainDriverPhone=m.main_driver_phone,
            mainDriverIdCard=m.main_driver_id_card,
            plateNumber=m.plate_number,
            trailerPlateNumber=m.trailer_plate_number,
            carrierName=m.carrier_name,
            carrierShortName=m.carrier_short_name,
            origin=m.origin,
            originCode=m.origin_code,
            originRegionId=m.origin_region_id,
            destination=m.destination,
            destinationCode=m.destination_code,
            destinationRegionId=m.destination_region_id,
            segmentCount=m.segment_count,
            totalQuantity=m.total_quantity,
            waybillCount=m.waybill_count,
            plannedLoadTime=m.planned_load_time,
            plannedArriveTime=m.planned_arrive_time,
            actualLoadTime=m.actual_load_time,
            actualArriveTime=m.actual_arrive_time,
            carrierCostAmount=(
                float(m.carrier_cost_amount)
                if m.carrier_cost_amount is not None else None
            ),
            carrierCostType=m.carrier_cost_type,
            costRemark=m.cost_remark,
            prepaidAmount=float(m.prepaid_amount or 0),
            supplementAmount=float(m.supplement_amount or 0),
            settledAmount=float(m.settled_amount or 0),
            financeDocCount=m.finance_doc_count,
            status=m.status,
            dispatcherId=m.dispatcher_id,
            dispatcherName=m.dispatcher_name,
            remark=m.remark,
            createdAt=m.created_at,
            updatedAt=m.updated_at,
            segments=[TaskSegmentOut.from_model(s) for s in (segments or [])],
            waybillItems=[
                TaskWaybillItemOut.from_model(w) for w in (waybill_items or [])
            ],
        )
