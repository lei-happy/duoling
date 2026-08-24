"""管理员小程序聚合接口：首页 KPI、统一速查。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.services.workbench.mp_home_service import MpHomeService

router = APIRouter()


def _require_tenant(current_user: TokenData) -> str:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")
    return current_user.tenant_code


@router.get("/mp-home")
async def mp_home(
    persona: Optional[str] = Query(None, description="dispatch / boss / finance / captain"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    data = await MpHomeService.home_summary(
        db, user_id=current_user.user_id, persona=persona
    )
    return success(data=data)


@router.get("/mp-lookup")
async def mp_lookup(
    keyword: str = Query("", min_length=0, max_length=40),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    data = await MpHomeService.lookup(db, keyword)
    return success(data=data)
