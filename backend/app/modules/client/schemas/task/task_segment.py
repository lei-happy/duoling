"""任务单运输分段 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskSegmentIn(BaseModel):
    """分段入参（创建/整单替换）"""
    segmentNo: int = Field(ge=1, le=20, description="段序号 1-20")
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


class TaskSegmentStatusUpdate(BaseModel):
    status: int = Field(ge=0, le=4)
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    remark: Optional[str] = None


class TaskSegmentOut(BaseModel):
    id: int
    taskId: int
    segmentNo: int
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
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "TaskSegmentOut":
        return cls(
            id=m.id,
            taskId=m.task_id,
            segmentNo=m.segment_no,
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
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
