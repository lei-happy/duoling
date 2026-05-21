"""任务单装卸记录 Schemas（多批次装/卸车）"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class TaskLoadingRecordItemIn(BaseModel):
    """装卸记录子项入参（关联 task_waybill_item）"""

    itemId: int = Field(ge=1, description="task_waybill_item.id")
    quantity: int = Field(
        ge=1,
        description="本次该 item 装/卸台数（本期默认 = item.quantity）",
    )


class TaskLoadingRecordCreate(BaseModel):
    """创建装卸记录入参"""

    eventType: int = Field(ge=1, le=2, description="1-装车 2-卸车")
    dispatchOrderId: Optional[int] = Field(
        default=None, description="关联调令 ID（多调令任务必填）"
    )
    happenedAt: datetime = Field(description="实际装/卸时间")
    location: Optional[str] = Field(default=None, max_length=255)
    locationCode: Optional[str] = Field(default=None, max_length=20)
    locationRegionId: Optional[int] = None
    items: List[TaskLoadingRecordItemIn] = Field(min_length=1)
    photoUrls: List[str] = Field(default_factory=list, max_length=9)
    remark: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _check_items(self):
        ids = [it.itemId for it in self.items]
        if len(set(ids)) != len(ids):
            raise ValueError("同一次装卸记录不允许重复挂接同一行 item")
        return self


class TaskLoadingRecordItemOut(BaseModel):
    id: int
    recordId: int
    itemId: int
    quantity: int
    waybillId: Optional[int] = None
    waybillNo: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_models(cls, ri, item) -> "TaskLoadingRecordItemOut":
        return cls(
            id=ri.id,
            recordId=ri.record_id,
            itemId=ri.item_id,
            quantity=int(ri.quantity or 0),
            waybillId=getattr(item, "waybill_id", None),
            waybillNo=getattr(item, "waybill_no", None),
            vehicleBrand=getattr(item, "vehicle_brand", None),
            vehicleModel=getattr(item, "vehicle_model", None),
        )


class TaskLoadingRecordOut(BaseModel):
    id: int
    taskId: int
    dispatchOrderId: Optional[int] = None
    eventType: int
    happenedAt: datetime
    location: Optional[str] = None
    locationCode: Optional[str] = None
    locationRegionId: Optional[int] = None
    quantity: int
    photoUrls: List[str] = Field(default_factory=list)
    operatorId: Optional[int] = None
    operatorName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime
    items: List[TaskLoadingRecordItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, items: Optional[List] = None) -> "TaskLoadingRecordOut":
        return cls(
            id=m.id,
            taskId=m.task_id,
            dispatchOrderId=m.dispatch_order_id,
            eventType=int(m.event_type),
            happenedAt=m.happened_at,
            location=m.location,
            locationCode=m.location_code,
            locationRegionId=m.location_region_id,
            quantity=int(m.quantity or 0),
            photoUrls=list(m.photo_urls or []),
            operatorId=m.operator_id,
            operatorName=m.operator_name,
            remark=m.remark,
            createdAt=m.created_at,
            items=list(items or []),
        )
