"""
企业自助注册接口（已下线）

官网自助注册会直接建库建租户，脚本刷几次就能造出一堆空租户。
现在开户统一改由顾问在运营端办理，这里的路由保留但只回引导文案：
旧书签、外部链接、爬虫都不会 404，同时彻底堵死自助建库这条路。

RegisterService 与 open_register_task 表暂时保留，留一轮观察期便于回滚。
"""

import re

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.common.exceptions import BizException
from app.modules.open.schemas.register import RegisterPhoneCheckOut
from app.modules.open.services.register_service import RegisterService

router = APIRouter()

_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")

_REGISTER_CLOSED = "开户已改为顾问协助办理，请在官网留下联系方式，我们 1 个工作日内回电。"


@router.get("/phone-available")
async def register_phone_available(
    phone: str = Query(..., min_length=11, max_length=11, description="手机号"),
    db: AsyncSession = Depends(get_platform_db),
):
    """查询手机号是否已关联企业（承运商邀请落地页仍在用，用于提示直接登录）"""
    if not _PHONE_RE.match(phone):
        raise BizException("请输入正确的手机号码")
    registered = await RegisterService.is_phone_registered(db, phone)
    out = RegisterPhoneCheckOut(registered=registered)
    return success(data=out.model_dump())


@router.post("")
async def register_tenant():
    """企业自助注册已下线，引导改走留资"""
    raise BizException(_REGISTER_CLOSED)


@router.get("/progress/{task_id}")
async def register_progress(task_id: str):
    """注册进度查询已下线（历史任务不再对外暴露）"""
    raise BizException(_REGISTER_CLOSED)
