"""
企业端驾驶员管理 API
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.core.security import TokenData
from app.core.database import db_manager
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.driver import (
    DriverCreate, DriverUpdate, DriverOut,
    DriverStatusUpdate, DriverOperationStatusUpdate,
)
from app.modules.client.services.driver import DriverService
from app.modules.console.services.driver.sys_driver_service import SysDriverService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _sync_to_platform(tenant_code: str, driver_out: DriverOut):
    """将司机摘要同步到平台库（fire-and-forget）"""
    try:
        async for platform_db in db_manager.get_platform_session():
            await SysDriverService.sync_driver(
                platform_db,
                tenant_code=tenant_code,
                biz_driver_id=driver_out.id,
                driver_code=driver_out.driverCode or "",
                name=driver_out.name or "",
                phone=driver_out.phone or "",
                status=driver_out.status if driver_out.status is not None else 1,
            )
    except Exception as e:
        logger.warning(f"平台司机同步失败: {e}")


async def _remove_from_platform(tenant_code: str, biz_driver_id: int):
    """从平台库软删除司机记录"""
    try:
        async for platform_db in db_manager.get_platform_session():
            await SysDriverService.remove_driver(
                platform_db,
                tenant_code=tenant_code,
                biz_driver_id=biz_driver_id,
            )
    except Exception as e:
        logger.warning(f"平台司机删除同步失败: {e}")


@router.get("")
async def page_drivers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    driverType: Optional[int] = None,
    operationStatus: Optional[int] = None,
    departmentId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverService.page_drivers(
        db, page=page, page_size=page_size,
        keyword=keyword, status=status,
        driver_type=driverType,
        operation_status=operationStatus,
        department_id=departmentId,
    )
    return success(data=data)


@router.get("/{driver_id}")
async def get_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverService.get_driver(db, driver_id)
    return success(data=data.model_dump())


@router.post("")
@operation_log(module="驾驶员管理", action="新增", description="新增驾驶员")
async def create_driver(
    request: Request,
    data: DriverCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    driver = await DriverService.create_driver(db, data)
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, driver)
    return success(data=driver.model_dump())


@router.put("/{driver_id}")
@operation_log(module="驾驶员管理", action="编辑", description="编辑驾驶员")
async def update_driver(
    request: Request,
    driver_id: int,
    data: DriverUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    driver = await DriverService.update_driver(db, driver_id, data)
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, driver)
    return success(data=driver.model_dump())


@router.delete("/{driver_id}")
@operation_log(module="驾驶员管理", action="删除", description="删除驾驶员")
async def delete_driver(
    request: Request,
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await DriverService.delete_driver(db, driver_id)
    if current_user.tenant_code:
        await _remove_from_platform(current_user.tenant_code, driver_id)
    return success()


@router.put("/{driver_id}/status")
@operation_log(module="驾驶员管理", action="状态变更", description="修改人事状态")
async def update_status(
    request: Request,
    driver_id: int,
    data: DriverStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    driver = await DriverService.update_status(db, driver_id, data.status)
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, driver)
    return success(data=driver.model_dump())


@router.put("/{driver_id}/operation-status")
@operation_log(module="驾驶员管理", action="运营状态变更", description="修改运营状态")
async def update_operation_status(
    request: Request,
    driver_id: int,
    data: DriverOperationStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    driver = await DriverService.update_operation_status(
        db, driver_id, data.operationStatus
    )
    return success(data=driver.model_dump())
