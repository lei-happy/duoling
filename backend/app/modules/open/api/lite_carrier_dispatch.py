"""LITE 端 - 承运商运力上报（占位实现）

仅作为接口契约的最小可用实现，详见
``项目文档/02.需求文档/03.LITE端/承运商运力上报.md``。

关键校验：
1. ``X-Lite-Token`` 必填（暂仅校验非空，后续接 JWT/HMAC 验签）
2. 路径参数 task_id 对应任务 ``carrier_type=2`` 且 ``status=0 待派车``
3. 通过后等价调用 ``TaskService.assign_carrier``，
   写入承运方运力快照并把 task 推进至 ``status=1 已派车``
"""

from typing import Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.response import success
from app.core.dependencies import get_tenant_db
from app.modules.client.schemas.task.task import (
    TaskAssignCarrierRequest,
    TaskCarrierInfo,
)
from app.modules.client.services.task.task_service import TaskService


router = APIRouter()


class LiteCarrierDispatchRequest(BaseModel):
    """承运商上报运力入参"""

    capacityId: Optional[int] = Field(
        default=None, description="承运商自有运力库 ID（可选）",
    )
    mainDriverName: str = Field(min_length=1, max_length=50)
    mainDriverPhone: str = Field(min_length=11, max_length=20)
    mainDriverIdCard: Optional[str] = Field(default=None, max_length=20)
    plateNumber: str = Field(min_length=2, max_length=20)
    trailerPlateNumber: Optional[str] = Field(default=None, max_length=20)


@router.post("/task/{task_id}/dispatch")
async def lite_carrier_dispatch(
    task_id: int,
    data: LiteCarrierDispatchRequest,
    x_lite_token: Optional[str] = Header(default=None, alias="X-Lite-Token"),
    db: AsyncSession = Depends(get_tenant_db),
):
    """承运商上报运力（lite 端） - 占位实现。

    实际签名校验、租户切换待 LITE 端落地时补齐。
    当前仅做：
    - X-Lite-Token 非空校验
    - 任务 carrier_type=2 / status=0 校验
    - 复用 TaskService.assign_carrier 完成 0→1 推进
    """
    if not x_lite_token or not x_lite_token.strip():
        raise BizException("缺少 lite token")

    task = await TaskService.get_or_404(db, task_id)
    if int(task.carrier_type or 0) != 2:
        raise BizException("仅承运商类型任务可由承运商上报运力")
    if int(task.status) != 0:
        raise BizException(
            f"任务当前状态={task.status}，不允许上报运力（仅 0 待派车）"
        )

    payload = TaskAssignCarrierRequest(
        carrier=TaskCarrierInfo(
            carrierType=2,
            carrierId=task.carrier_id,
            capacityId=data.capacityId,
            mainDriverName=data.mainDriverName,
            mainDriverPhone=data.mainDriverPhone,
            mainDriverIdCard=data.mainDriverIdCard,
            plateNumber=data.plateNumber,
            trailerPlateNumber=data.trailerPlateNumber,
            carrierName=task.carrier_name,
        ),
        isProxy=False,
    )
    updated = await TaskService.assign_carrier(db, task_id, payload)
    return success(data={
        "taskId": updated.id,
        "taskNo": updated.task_no,
        "status": updated.status,
        "dispatchedAt": updated.updated_at,
    })
