"""驾驶员任务相关 Schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 司机动作请求
# ============================================================

class DriverConfirmLoadRequest(BaseModel):
    """确认装车请求（薄层包装：通过创建装车记录 event_type=1 推进 item.status=1）。"""

    actualLoadTime: Optional[datetime] = Field(
        default=None, description="实际装车时间（不传则取当前服务器时间）"
    )
    location: Optional[str] = Field(default=None, max_length=255, description="装车地点")
    photoUrls: List[str] = Field(default_factory=list, max_length=9, description="装车照片")
    remark: Optional[str] = Field(default=None, max_length=255)


class DriverDepartRequest(BaseModel):
    """确认出发请求（task 2→3）。"""

    actualLoadTime: Optional[datetime] = None
    remark: Optional[str] = Field(default=None, max_length=255)


class DriverConfirmArriveRequest(BaseModel):
    """确认到达请求（创建卸车记录 event_type=2 推进 item.status=2，聚合到 task 3→4）。"""

    actualArriveTime: Optional[datetime] = Field(
        default=None, description="实际到达时间"
    )
    location: Optional[str] = Field(default=None, max_length=255, description="卸车地点")
    photoUrls: List[str] = Field(default_factory=list, max_length=9, description="卸车照片")
    remark: Optional[str] = Field(default=None, max_length=255)


class DriverSignItemRequest(BaseModel):
    """单条挂接行签收（item 2/1/0→3，聚合驱动 task 4→5）。"""

    signedAt: Optional[datetime] = Field(default=None, description="签收时间")
    remark: Optional[str] = Field(default=None, max_length=255)


class DriverRevertSignRequest(BaseModel):
    """撤销签收（item 3→2）；reason 必填。"""

    reason: str = Field(min_length=1, max_length=255, description="撤销原因")


# ============================================================
# 任务返回 Schemas
# ============================================================

class DriverTaskListItem(BaseModel):
    """司机任务列表项（精简字段）"""

    id: int
    taskNo: str
    taskName: Optional[str] = None
    status: int
    origin: Optional[str] = None
    destination: Optional[str] = None
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    totalQuantity: int = 0
    waybillCount: int = 0
    customerName: Optional[str] = None
    mainDriverName: Optional[str] = None
    plateNumber: Optional[str] = None
    carrierType: int = 1
    prepaidAmount: float = 0
    settledAmount: float = 0
    carrierCostAmount: Optional[float] = None


class DriverTaskItem(BaseModel):
    """任务下挂接的运单货物行"""

    id: int
    waybillId: int
    waybillNo: Optional[str] = None
    customerName: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    dealerName: Optional[str] = None
    quantity: int
    status: int
    loadedAt: Optional[datetime] = None
    unloadedAt: Optional[datetime] = None
    signedAt: Optional[datetime] = None


class DriverTaskSegment(BaseModel):
    """任务运输调令/段（保留对前端的最小展示字段）"""

    id: int
    segmentNo: int
    fromLocation: Optional[str] = None
    toLocation: Optional[str] = None
    plannedLoadTime: Optional[datetime] = None
    plannedArriveTime: Optional[datetime] = None
    actualLoadTime: Optional[datetime] = None
    actualArriveTime: Optional[datetime] = None
    status: int = 0
    mileage: Optional[float] = None


class DriverTaskDetail(DriverTaskListItem):
    """任务详情（含明细行与段）"""

    segments: List[DriverTaskSegment] = Field(default_factory=list)
    items: List[DriverTaskItem] = Field(default_factory=list)
    remark: Optional[str] = None
