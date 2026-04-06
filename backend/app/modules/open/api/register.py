"""
企业自助注册接口
"""

import re

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.common.exceptions import BizException
from app.modules.open.schemas.register import (
    RegisterSubmitRequest,
    RegisterPhoneCheckOut,
)
from app.modules.open.services.register_service import RegisterService

router = APIRouter()

_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


@router.get("/phone-available")
async def register_phone_available(
    phone: str = Query(..., min_length=11, max_length=11, description="手机号"),
    db: AsyncSession = Depends(get_platform_db),
):
    """查询手机号是否已关联企业（官网用于即时提示；仅 sys_user 无企业关联时不视为已注册）"""
    if not _PHONE_RE.match(phone):
        raise BizException("请输入正确的手机号码")
    registered = await RegisterService.is_phone_registered(db, phone)
    out = RegisterPhoneCheckOut(registered=registered)
    return success(data=out.model_dump())


@router.post("")
async def register_tenant(
    data: RegisterSubmitRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_platform_db),
):
    """企业自助注册：立即返回 task_id，客户端轮询 /register/progress/{task_id}"""
    result = await RegisterService.start_register(db, data, background_tasks)
    return success(data=result.model_dump(), message="已受理注册")


@router.get("/progress/{task_id}")
async def register_progress(
    task_id: str,
    db: AsyncSession = Depends(get_platform_db),
):
    """查询企业注册任务进度与结果"""
    out = await RegisterService.get_progress(db, task_id)
    return success(data=out.model_dump())
