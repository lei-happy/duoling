"""任务单主表 Schemas"""

from datetime import datetime
from typing import List, Mapping, Optional

from pydantic import BaseModel, Field, model_validator

from app.modules.client.schemas.task.task_dispatch_order import (
    TaskDispatchOrderIn, TaskDispatchOrderOut,
)
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemIn, TaskWaybillItemOut,
)


# 兼容旧引用（前端仍可能用 segments/segmentNo 字段名提交）
TaskSegmentIn = TaskDispatchOrderIn
TaskSegmentOut = TaskDispatchOrderOut


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


class TaskCarrierAssignmentInfo(BaseModel):
    """待分配阶段：确定承运方式（及承运商/社会运力身份；自有车可仅选方式）。

    提交后任务进入「待派车」(status=0)，具体运力在派车环节确认。
    """
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
        if self.carrierType == 2:
            if not (self.carrierId or (self.carrierName and self.carrierName.strip())):
                raise ValueError("承运商任务必须选择承运商或填写承运商名称")
        elif self.carrierType == 3:
            if not (
                self.mainDriverName
                and self.mainDriverPhone
                and self.plateNumber
            ):
                raise ValueError("社会运力必须填写司机姓名/电话/车牌")
        return self


class TaskCreate(BaseModel):
    """创建任务单

    分阶段创建：
    - 必填：waybillItems（商品车挂接，至少 1 条）
    - 可选：carrier（不填则任务保存为「待分配」status=-1；填则同步派车至 status=1）
    - 可选：segments（不填则任务无分段，task.origin/destination 由 waybillItems 兜底；
            后续可通过 POST /business/task/{id}/plan-route 补齐分段路线）
    """
    taskNo: Optional[str] = None
    taskName: Optional[str] = None
    source: int = 1
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    carrierCostType: Optional[int] = None
    carrierCostAmount: Optional[float] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None

    # 承运方（可选，未填则保存为「待分配」）
    carrier: Optional[TaskCarrierInfo] = None

    # 调令路线（可选，零段允许，仅校验非空时段号连续；前端字段名仍为 segments）
    segments: List[TaskDispatchOrderIn] = Field(default_factory=list)
    # 至少 1 条挂接
    waybillItems: List[TaskWaybillItemIn] = Field(
        default_factory=list, min_length=1
    )

    @model_validator(mode="after")
    def _check_segments(self):
        if not self.segments:
            return self
        nos = [s.orderNo for s in self.segments]
        if len(set(nos)) != len(nos):
            raise ValueError("调令序号不允许重复")
        if sorted(nos) != list(range(1, len(nos) + 1)):
            raise ValueError("调令序号必须从 1 开始连续")
        return self


class TaskUpdate(BaseModel):
    """更新任务单（status=-1/0/1 时允许）"""
    taskName: Optional[str] = None
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    carrierCostType: Optional[int] = None
    carrierCostAmount: Optional[float] = None
    costRemark: Optional[str] = None
    remark: Optional[str] = None
    carrier: Optional[TaskCarrierInfo] = None
    segments: Optional[List[TaskDispatchOrderIn]] = None
    waybillItems: Optional[List[TaskWaybillItemIn]] = None


class TaskStatusUpdate(BaseModel):
    status: int = Field(ge=0, le=9)
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    signedAt: Optional[datetime] = Field(
        default=None,
        description="客户签收时间（仅 status=5 时生效；用于 propagate 到 item.signed_at）",
    )
    remark: Optional[str] = None


class TaskAssignCarrierRequest(BaseModel):
    """派车（设置承运方）。

    待派车阶段的"指派具体运力"动作。当承运方为承运商（carrierType=2）时，
    本期 lite 端尚未上线，前端面板提供 ``isProxy=true`` 的"调度员代填"兜底，
    后端不做区分（同样是写入承运方快照 + 状态 0→1），仅作审计标识。
    """
    carrier: TaskCarrierInfo
    isProxy: bool = Field(
        default=False,
        description="标识是否为调度员代承运商代填运力（兜底，本期 lite 未上线时使用）",
    )
    carrierCostType: Optional[int] = None
    carrierCostAmount: Optional[float] = None
    costRemark: Optional[str] = None


class TaskPlanRouteRequest(BaseModel):
    """规划路线（替换调令）

    仅用于已存在的任务单补齐 / 重做调令规划；不影响承运方与商品车挂接。
    至少 1 条调令；调令序号必须从 1 开始连续。
    """
    segments: List[TaskDispatchOrderIn] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_segments(self):
        nos = [s.orderNo for s in self.segments]
        if len(set(nos)) != len(nos):
            raise ValueError("调令序号不允许重复")
        if sorted(nos) != list(range(1, len(nos) + 1)):
            raise ValueError("调令序号必须从 1 开始连续")
        return self


class TaskCancelRequest(BaseModel):
    reason: Optional[str] = None


class TaskRevertStatusRequest(BaseModel):
    """撤销至上一态（专项接口）。"""
    targetStatus: int = Field(ge=0, le=7, description="目标态，需在反向跳转表内")
    reason: str = Field(min_length=2, max_length=500, description="撤销原因（必填）")


class TaskForceCancelRequest(BaseModel):
    """强制取消（线下取消，2/3/4 → 9）。"""
    reason: str = Field(min_length=2, max_length=500, description="强制取消原因（必填）")
    cancelUnpaidFinanceDocs: bool = Field(
        default=True, description="是否一并撤销该任务下所有未支付费用单（默认 True）",
    )


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
    loadedQuantity: int = Field(default=0, description="已装车台数（聚合 item.status>=1）")
    unloadedQuantity: int = Field(default=0, description="已卸车台数（聚合 item.status>=2）")
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
    def from_model(
        cls,
        m,
        *,
        loaded_quantity: int = 0,
        unloaded_quantity: int = 0,
    ) -> "TaskListItemOut":
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
            loadedQuantity=int(loaded_quantity or 0),
            unloadedQuantity=int(unloaded_quantity or 0),
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

    segments: List[TaskDispatchOrderOut] = Field(default_factory=list)
    waybillItems: List[TaskWaybillItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        m,
        segments: Optional[list] = None,
        waybill_items: Optional[list] = None,
        *,
        series_lookup: Optional[Mapping[str, Optional[str]]] = None,
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
            segments=[TaskDispatchOrderOut.from_model(s) for s in (segments or [])],
            waybillItems=[
                TaskWaybillItemOut.from_model(w, series_lookup=series_lookup)
                for w in (waybill_items or [])
            ],
        )
