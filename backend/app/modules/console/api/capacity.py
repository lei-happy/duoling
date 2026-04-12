"""
管理后台 - 平台运力列表 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.services.capacity.sys_capacity_service import SysCapacityService

router = APIRouter()


@router.get("")
async def page_capacities(
    page: int = Query(1),
    limit: int = Query(20),
    keyword: Optional[str] = Query(None),
    tenantCode: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询平台运力列表"""
    result = await SysCapacityService.page_capacities(
        db,
        page=page,
        limit=limit,
        keyword=keyword,
        tenant_code=tenantCode,
        status=status,
    )
    return success(data=result)


@router.get("/{capacity_id}")
async def get_capacity(
    capacity_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查看平台运力详情"""
    data = await SysCapacityService.get_capacity(db, capacity_id)
    if not data:
        return fail(message="记录不存在")
    return success(data=data)
