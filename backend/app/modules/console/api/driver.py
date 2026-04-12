"""
管理后台 - 平台司机列表 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.services.driver.sys_driver_service import SysDriverService

router = APIRouter()


@router.get("")
async def page_drivers(
    page: int = Query(1),
    limit: int = Query(20),
    keyword: Optional[str] = Query(None),
    tenantCode: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询平台司机列表"""
    result = await SysDriverService.page_drivers(
        db,
        page=page,
        limit=limit,
        keyword=keyword,
        tenant_code=tenantCode,
        status=status,
    )
    return success(data=result)


@router.get("/{driver_id}")
async def get_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查看平台司机详情"""
    data = await SysDriverService.get_driver(db, driver_id)
    if not data:
        return fail(message="记录不存在")
    return success(data=data)
