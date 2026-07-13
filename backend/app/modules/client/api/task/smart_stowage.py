"""
企业端智能配载 API（专业版 feature: smart_stowage）

接口前缀：/business/smart-stowage
- 一键生成配载方案（同步产出）
- 查询生成任务状态 / 方案列表
- 采纳方案 -> 复用建单落为 biz_task(source=2)
- 忽略方案
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.task.smart_stowage import (
    SmartStowageAdoptRequest,
    SmartStowageGenerateRequest,
    SmartStowagePlanOut,
    SmartStowageTaskOut,
)
from app.modules.client.services.company_activity_service import (
    CompanyActivityService,
)
from app.modules.client.services.task.smart_stowage.smart_stowage_service import (
    SmartStowageService,
)
from app.modules.client.services.task.smart_stowage.stowage_task_service import (
    SmartStowageTaskService,
)

router = APIRouter()


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


@router.post("/generate")
@operation_log(module="智能配载", action="生成方案", description="智能配载生成方案")
async def generate_plans(
    request: Request,
    data: SmartStowageGenerateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    filter_payload = {
        "keyword": data.keyword,
        "customerId": data.customerId,
        "originKeyword": data.originKeyword,
        "destinationKeyword": data.destinationKeyword,
        "modelKeyword": data.modelKeyword,
        "limit": data.limit,
    }
    params_payload = {
        "targetSpots": data.targetSpots,
        "minLoadRate": data.minLoadRate,
        "maxPlans": data.maxPlans,
        "weights": data.weights,
        "occupyOverrides": data.occupyOverrides,
    }
    task_id = await SmartStowageService.generate_sync(
        db,
        filter_payload=filter_payload,
        params_payload=params_payload,
        current_user_id=current_user.user_id,
        user_name=op_name,
    )
    task = await SmartStowageTaskService.get(db, task_id)
    plans = await SmartStowageService.list_plans(db, task_id)
    return success(data={
        "task": SmartStowageTaskOut.from_model(task).model_dump(),
        "plans": [SmartStowagePlanOut(**p).model_dump() for p in plans],
    })


@router.get("/tasks/{task_id}")
async def get_generation_task(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await SmartStowageTaskService.get(db, task_id)
    if task is None:
        return success(data=None)
    return success(data=SmartStowageTaskOut.from_model(task).model_dump())


@router.get("/plans")
async def list_plans(
    planTaskId: int = Query(..., description="生成任务ID"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    plans = await SmartStowageService.list_plans(db, planTaskId)
    return success(data=[SmartStowagePlanOut(**p).model_dump() for p in plans])


@router.post("/plans/{plan_id}/adopt")
@operation_log(module="智能配载", action="采纳方案", description="采纳智能配载方案")
async def adopt_plan(
    request: Request,
    plan_id: int,
    data: SmartStowageAdoptRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    task_id = await SmartStowageService.adopt_plan(
        db, plan_id,
        remark=data.remark,
        current_user_id=current_user.user_id,
        dispatcher_name=op_name,
    )
    return success(data={"taskId": task_id})


@router.post("/plans/{plan_id}/ignore")
@operation_log(module="智能配载", action="忽略方案", description="忽略智能配载方案")
async def ignore_plan(
    request: Request,
    plan_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await SmartStowageService.ignore_plan(db, plan_id)
    return success()
