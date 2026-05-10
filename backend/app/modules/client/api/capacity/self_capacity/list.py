"""
自有运力-运力列表 API

负责司机与车辆的绑定关系（上车/下车）：
  - GET    /              分页查询
  - POST   /bind          上车（绑定）
  - PUT    /{id}/unbind   下车（解绑）
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import (
    get_tenant_db,
    get_current_user,
    ensure_biz_company_activity_table,
)
from app.core.security import TokenData
from app.core.database import db_manager
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.capacity.self_capacity.capacity import (
    CapacityBind, CapacityUnbind,
)
from app.modules.client.services.capacity.self_capacity.capacity_service import (
    CapacityService,
)
from app.modules.console.services.capacity.sys_capacity_service import SysCapacityService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _sync_to_platform(tenant_code: str, capacity_out):
    """将运力摘要同步到平台库（fire-and-forget）"""
    try:
        async for platform_db in db_manager.get_platform_session():
            await SysCapacityService.sync_capacity(
                platform_db,
                tenant_code=tenant_code,
                biz_capacity_id=capacity_out.id,
                driver_name=capacity_out.driverName or "",
                driver_phone=capacity_out.driverPhone or "",
                plate_number=capacity_out.plateNumber or "",
                status=capacity_out.status,
                bound_at=capacity_out.boundAt,
                unbound_at=capacity_out.unboundAt,
            )
    except Exception as e:
        logger.warning(f"平台运力同步失败: {e}")


@router.get("")
async def page_capacities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """运力分页列表（仅绑定中；已解绑见变动记录）"""
    data = await CapacityService.page_capacities(
        db, page=page, page_size=page_size, keyword=keyword,
    )
    return success(data=data)


@router.post("/bind")
@operation_log(module="运力管理", action="新建运力", description="绑定司机与车辆")
async def bind_capacity(
    request: Request,
    data: CapacityBind,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """上车（绑定司机+车辆）"""
    result = await CapacityService.bind(
        db,
        driver_id=data.driverId,
        vehicle_id=data.vehicleId,
        operator_user_id=current_user.user_id,
        remark=data.remark,
    )
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, result)
    return success(data=result.model_dump())


@router.put("/{capacity_id}/unbind")
@operation_log(module="运力管理", action="下车", description="解绑司机与车辆")
async def unbind_capacity(
    request: Request,
    capacity_id: int,
    data: CapacityUnbind,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """下车（解绑司机与车辆）"""
    result = await CapacityService.unbind(
        db,
        capacity_id=capacity_id,
        operator_user_id=current_user.user_id,
        remark=data.remark,
    )
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, result)
    return success(data=result.model_dump())
