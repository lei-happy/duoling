"""任务单调令 Schemas（原 task_segment 重命名扩展）"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from app.modules.client.services.state_machine.dispatch_order_state_machine import (
    DISPATCH_ORDER_NO_MAX,
    DISPATCH_ORDER_NO_MIN,
    DISPATCH_ORDER_STATUS_MAX,
    DISPATCH_ORDER_STATUS_MIN,
    DISPATCH_TYPE_DEFAULT,
    DISPATCH_TYPE_MAX,
    DISPATCH_TYPE_MIN,
)


class TaskDispatchOrderIn(BaseModel):
    """调令入参（创建/整单替换）

    兼容旧前端字段：``segmentNo`` 仍可被接受并自动映射到 ``orderNo``。
    """

    orderNo: int = Field(
        ge=DISPATCH_ORDER_NO_MIN, le=DISPATCH_ORDER_NO_MAX,
        description=f"调令序号 {DISPATCH_ORDER_NO_MIN}-{DISPATCH_ORDER_NO_MAX}",
    )
    dispatchType: int = Field(
        default=DISPATCH_TYPE_DEFAULT, ge=DISPATCH_TYPE_MIN, le=DISPATCH_TYPE_MAX,
        description="调令类型 1-重驶 2-空驶 3-年检 4-应急 5-其他",
    )
    fromLocation: Optional[str] = None
    fromCode: Optional[str] = None
    fromRegionId: Optional[int] = None
    toLocation: Optional[str] = None
    toCode: Optional[str] = None
    toRegionId: Optional[int] = None
    mileage: Optional[float] = None
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    remark: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _alias_segment_no(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if "orderNo" not in data and "segmentNo" in data:
            data = {**data, "orderNo": data["segmentNo"]}
        return data


class TaskDispatchOrderStatusUpdate(BaseModel):
    status: int = Field(
        ge=DISPATCH_ORDER_STATUS_MIN, le=DISPATCH_ORDER_STATUS_MAX,
        description="调令状态 0-待装车 1-装车中 2-在途 3-已到达 4-已卸车",
    )
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    acceptedAt: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    remark: Optional[str] = None


class TaskDispatchOrderOut(BaseModel):
    id: int
    taskId: int
    orderNo: int
    # 兼容旧前端：与 orderNo 等价，便于平滑迁移
    segmentNo: int
    dispatchType: int
    fromLocation: Optional[str] = None
    fromCode: Optional[str] = None
    fromRegionId: Optional[int] = None
    toLocation: Optional[str] = None
    toCode: Optional[str] = None
    toRegionId: Optional[int] = None
    mileage: Optional[float] = None
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    acceptedAt: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "TaskDispatchOrderOut":
        return cls(
            id=m.id,
            taskId=m.task_id,
            orderNo=m.order_no,
            segmentNo=m.order_no,
            dispatchType=int(m.dispatch_type or 1),
            fromLocation=m.from_location,
            fromCode=m.from_code,
            fromRegionId=m.from_region_id,
            toLocation=m.to_location,
            toCode=m.to_code,
            toRegionId=m.to_region_id,
            mileage=float(m.mileage) if m.mileage is not None else None,
            plannedLoadTime=m.planned_load_time,
            plannedArriveTime=m.planned_arrive_time,
            actualLoadTime=m.actual_load_time,
            actualArriveTime=m.actual_arrive_time,
            acceptedAt=m.accepted_at,
            startedAt=m.started_at,
            completedAt=m.completed_at,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
