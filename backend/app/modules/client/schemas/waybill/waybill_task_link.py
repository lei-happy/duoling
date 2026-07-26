"""计划关联任务（只读视图）"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WaybillLinkedTaskItemOut(BaseModel):
    """本计划在某任务下的挂接明细行"""

    id: int
    quantity: int
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    itemStatus: int = Field(description="挂接货物状态（item.status）")


class WaybillLinkedTaskOut(BaseModel):
    """本计划关联的单个任务（按任务聚合）"""

    taskId: int
    taskNo: str
    taskStatus: int
    mainDriverName: Optional[str] = None
    mainDriverPhone: Optional[str] = None
    plateNumber: Optional[str] = None
    allocatedQuantity: int = Field(
        description="本计划在该任务下占用的总台数",
    )
    items: List[WaybillLinkedTaskItemOut] = Field(default_factory=list)


class WaybillLinkedTasksOut(BaseModel):
    """计划关联任务列表"""

    waybillId: int
    waybillNo: str
    tasks: List[WaybillLinkedTaskOut] = Field(default_factory=list)
