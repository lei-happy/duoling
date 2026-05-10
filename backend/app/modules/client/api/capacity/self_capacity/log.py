"""
自有运力-变更记录 API

  - GET / 分页查询运力变动历史
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.services.capacity.self_capacity.capacity_service import (
    CapacityService,
)

router = APIRouter()


@router.get("")
async def page_capacity_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    action: Optional[int] = None,
    operatorName: Optional[str] = Query(None),
    actionTimeStart: Optional[str] = Query(None),
    actionTimeEnd: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """运力变动历史分页列表"""
    data = await CapacityService.page_logs(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        action=action,
        operator_name=operatorName,
        action_time_start=actionTimeStart,
        action_time_end=actionTimeEnd,
    )
    return success(data=data)
