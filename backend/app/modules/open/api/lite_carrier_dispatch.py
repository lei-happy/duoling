"""LITE 端 - 承运商运力上报（占位实现）

仅作为接口契约的最小可用实现，详见
``项目文档/02.需求文档/03.LITE端/承运商运力上报.md``。

关键校验：
1. ``X-Lite-Token`` 必填（暂仅校验非空，后续接 JWT/HMAC 验签）
2. 从 token / 查询参数解析 ``tenant_code``，显式获取租户库（不依赖 JWT 中间件）
3. 路径参数 task_id 对应任务 ``carrier_type=2`` 且 ``status=0 待派车``
4. 通过后等价调用 ``TaskService.assign_carrier``，
   写入承运方运力快照并把 task 推进至 ``status=1 已派车``
"""

from typing import Optional

from fastapi import APIRouter, Header, Query
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.response import success
from app.core.config import get_settings
from app.core.database import db_manager
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


def _parse_lite_tenant_code(
    x_lite_token: Optional[str],
    tenant_code_param: Optional[str] = None,
) -> str:
    """从 X-Lite-Token（JWT 载荷）或查询参数 tenant_code 解析租户编码。"""
    if not x_lite_token or not x_lite_token.strip():
        raise BizException("缺少 lite token")

    token = x_lite_token.strip()
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        tc = payload.get("tenant_code") or payload.get("tenant")
        if tc:
            return str(tc).strip()
    except JWTError:
        pass

    if tenant_code_param and str(tenant_code_param).strip():
        return str(tenant_code_param).strip()

    raise BizException("无法从 lite token 解析租户信息")


@router.post("/task/{task_id}/dispatch")
async def lite_carrier_dispatch(
    task_id: int,
    data: LiteCarrierDispatchRequest,
    x_lite_token: Optional[str] = Header(default=None, alias="X-Lite-Token"),
    tenant_code: Optional[str] = Query(
        default=None,
        description="占位：非 JWT token 时显式指定租户编码",
    ),
):
    """承运商上报运力（lite 端） - 占位实现。

    实际签名校验、租户切换待 LITE 端落地时补齐。
    当前：
    - X-Lite-Token 非空校验
    - 从 token / tenant_code 参数解析租户并显式切库
    - 任务 carrier_type=2 / status=0 校验
    - 复用 TaskService.assign_carrier 完成 0→1 推进
    """
    tc = _parse_lite_tenant_code(x_lite_token, tenant_code)

    async for db in db_manager.get_tenant_session(tc):
        return await _dispatch_on_tenant_db(
            db, task_id, data, x_lite_token.strip()
        )


async def _dispatch_on_tenant_db(
    db: AsyncSession,
    task_id: int,
    data: LiteCarrierDispatchRequest,
    x_lite_token: str,
) -> dict:
    """在已解析的租户库 session 内执行运力上报（便于单测）。"""
    _ = x_lite_token  # 占位：后续 JWT/HMAC 验签使用

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
