"""
自有运力-驾驶员管理 API
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
from app.modules.client.schemas.capacity.self_capacity.driver import (
    DriverCreate, DriverUpdate, DriverOut,
    DriverStatusUpdate, DriverOperationStatusUpdate,
)
from app.modules.client.services.capacity.self_capacity.driver import DriverService
from app.modules.client.services.capacity.self_capacity.driver.driver_account_sync import (
    AccountSyncResult,
    DriverPlatformAccountSync,
)
from app.modules.console.services.driver.sys_driver_service import SysDriverService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _sync_to_platform(tenant_code: str, driver_out: DriverOut):
    """将驾驶员摘要同步到平台库（fire-and-forget）"""
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
        logger.warning(f"平台驾驶员同步失败: {e}")


async def _sync_login_account(
    tenant_code: str, tenant_db: AsyncSession, driver_id: int
) -> Optional[AccountSyncResult]:
    """创建/编辑驾驶员后开通或刷新 H5 登录账号（fire-and-forget，不阻断主流程）。

    注意：不能在 ``async for`` 中提前 return，否则平台库 Session 不会 commit。
    """
    result: Optional[AccountSyncResult] = None
    try:
        async for platform_db in db_manager.get_platform_session():
            result = await DriverPlatformAccountSync.sync_account(
                platform_db, tenant_db, tenant_code, driver_id
            )
    except Exception as e:
        logger.warning(f"驾驶员登录账号开通失败: {e}")
    return result


async def _sync_login_status(
    tenant_code: str, tenant_db: AsyncSession, driver_id: int
) -> None:
    """人事状态变更后同步登录账号启用/停用。"""
    try:
        async for platform_db in db_manager.get_platform_session():
            await DriverPlatformAccountSync.sync_status(
                platform_db, tenant_db, tenant_code, driver_id
            )
    except Exception as e:
        logger.warning(f"驾驶员登录账号状态同步失败: {e}")


async def _close_login_account(
    tenant_code: str, user_id: Optional[int], phone: Optional[str]
) -> None:
    """删除驾驶员时软删本企业登录关联。"""
    try:
        async for platform_db in db_manager.get_platform_session():
            await DriverPlatformAccountSync.close_account(
                platform_db, tenant_code, user_id, phone
            )
    except Exception as e:
        logger.warning(f"驾驶员登录账号关闭失败: {e}")


def _attach_account(data: dict, result: Optional[AccountSyncResult]) -> dict:
    """把账号开通结果并入返回数据，供前端展示登录账号状态与冲突提示。"""
    data["loginAccount"] = {
        "opened": bool(result.opened) if result else False,
        "userId": result.user_id if result else data.get("userId"),
        "conflict": bool(result.conflict) if result else False,
        "message": result.message if result else "",
    }
    return data


async def _remove_from_platform(tenant_code: str, biz_driver_id: int):
    """从平台库软删除驾驶员记录"""
    try:
        async for platform_db in db_manager.get_platform_session():
            await SysDriverService.remove_driver(
                platform_db,
                tenant_code=tenant_code,
                biz_driver_id=biz_driver_id,
            )
    except Exception as e:
        logger.warning(f"平台驾驶员删除同步失败: {e}")


@router.get("")
async def page_drivers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    driverType: Optional[str] = None,
    operationStatus: Optional[int] = None,
    departmentId: Optional[int] = None,
    enterpriseId: Optional[int] = Query(None),
    sort: Optional[str] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await DriverService.page_drivers(
        db, page=page, page_size=page_size,
        keyword=keyword, status=status,
        driver_type=driverType,
        operation_status=operationStatus,
        department_id=departmentId,
        enterprise_id=enterpriseId,
        sort=sort,
        order=order,
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
    acct: Optional[AccountSyncResult] = None
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, driver)
        acct = await _sync_login_account(current_user.tenant_code, db, driver.id)
    data_out = _attach_account(driver.model_dump(), acct)
    msg = "操作成功"
    if acct and acct.conflict:
        msg = acct.message
    return success(data=data_out, message=msg)


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
    acct: Optional[AccountSyncResult] = None
    if current_user.tenant_code:
        await _sync_to_platform(current_user.tenant_code, driver)
        acct = await _sync_login_account(current_user.tenant_code, db, driver.id)
    data_out = _attach_account(driver.model_dump(), acct)
    msg = "操作成功"
    if acct and acct.conflict:
        msg = acct.message
    return success(data=data_out, message=msg)


@router.delete("/{driver_id}")
@operation_log(module="驾驶员管理", action="删除", description="删除驾驶员")
async def delete_driver(
    request: Request,
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    # 删除前取出 user_id / phone，用于软删平台登录关联
    login_user_id: Optional[int] = None
    login_phone: Optional[str] = None
    try:
        existing = await DriverService.get_driver(db, driver_id)
        login_user_id = getattr(existing, "userId", None)
        login_phone = getattr(existing, "phone", None)
    except Exception:
        pass

    await DriverService.delete_driver(db, driver_id)
    if current_user.tenant_code:
        await _remove_from_platform(current_user.tenant_code, driver_id)
        await _close_login_account(
            current_user.tenant_code, login_user_id, login_phone
        )
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
        await _sync_login_status(current_user.tenant_code, db, driver_id)
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


@router.post("/{driver_id}/reset-password")
@operation_log(module="驾驶员管理", action="重置密码", description="重置驾驶员登录密码")
async def reset_login_password(
    request: Request,
    driver_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """将驾驶员 H5 登录密码重置为默认密码，并要求首次登录改密。"""
    result: Optional[AccountSyncResult] = None
    if current_user.tenant_code:
        try:
            async for platform_db in db_manager.get_platform_session():
                result = await DriverPlatformAccountSync.reset_password(
                    platform_db, db, current_user.tenant_code, driver_id
                )
        except Exception as e:
            logger.warning(f"驾驶员登录密码重置失败: {e}")
    if not result or not result.opened:
        return success(
            data={"reset": False},
            message=(result.message if result else "重置失败"),
        )
    return success(data={"reset": True}, message=result.message)
