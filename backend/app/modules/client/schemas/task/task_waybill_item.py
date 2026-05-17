"""任务单-运单货物挂接 Schemas"""

from datetime import datetime
from typing import Mapping, Optional

from pydantic import BaseModel, Field

from app.modules.client.schemas.waybill.waybill import waybill_brand_model_key


class TaskWaybillItemIn(BaseModel):
    """挂接入参（创建/批量替换）

    waybillId / waybillCargoId / quantity 三者必填；
    segmentId 可选指定走某段（默认 NULL 跟随主任务）。
    """
    waybillId: int = Field(ge=1)
    waybillCargoId: int = Field(ge=1)
    quantity: int = Field(ge=1)
    segmentId: Optional[int] = None
    remark: Optional[str] = None


class TaskWaybillItemStatusUpdate(BaseModel):
    status: int = Field(ge=0, le=3)
    loadedAt: Optional[datetime] = None
    unloadedAt: Optional[datetime] = None
    signedAt: Optional[datetime] = None
    segmentId: Optional[int] = None
    remark: Optional[str] = None


class TaskWaybillItemOut(BaseModel):
    id: int
    taskId: int
    waybillId: int
    waybillCargoId: int
    waybillNo: Optional[str] = None
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    dealerName: Optional[str] = None
    seriesImage: Optional[str] = Field(
        default=None,
        description="车系图（列表/明细由品牌+车型匹配 biz_vehicle_series，与运单侧一致）",
    )
    quantity: int
    segmentId: Optional[int] = None
    status: int
    loadedAt: Optional[datetime] = None
    unloadedAt: Optional[datetime] = None
    signedAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        m,
        *,
        series_lookup: Optional[Mapping[str, Optional[str]]] = None,
    ) -> "TaskWaybillItemOut":
        series_image = None
        if series_lookup is not None:
            series_image = series_lookup.get(
                waybill_brand_model_key(m.vehicle_brand, m.vehicle_model)
            )
        return cls(
            id=m.id,
            taskId=m.task_id,
            waybillId=m.waybill_id,
            waybillCargoId=m.waybill_cargo_id,
            waybillNo=m.waybill_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            vehicleBrand=m.vehicle_brand,
            vehicleModel=m.vehicle_model,
            dealerName=m.dealer_name,
            seriesImage=series_image,
            quantity=m.quantity,
            segmentId=m.segment_id,
            status=m.status,
            loadedAt=m.loaded_at,
            unloadedAt=m.unloaded_at,
            signedAt=m.signed_at,
            remark=m.remark,
            createdAt=m.created_at,
        )


class CandidateCargoOut(BaseModel):
    """挂接器左栏：可挂接的运单 cargo 候选行"""
    waybillId: int
    waybillNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    dealerName: Optional[str] = None
    requiredLoadTime: Optional[datetime] = None
    waybillStatus: int
    cargoId: int
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    seriesImage: Optional[str] = Field(
        default=None,
        description="车系图（与基础数据品牌+车系匹配，供前端展示）",
    )
    quantity: int = Field(description="cargo 行原始台数")
    allocatedQuantity: int = Field(description="已分配台数")
    remainingQuantity: int = Field(description="剩余可分配台数 = quantity - allocated")
