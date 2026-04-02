"""
日志中心 - 操作日志查询接口

提供对租户端操作日志的集中查询能力
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.models.common.operation_log import OperationLog
from app.modules.console.schemas.log_center.operation_log import OperationLogOut
from app.modules.console.services.log_center.operation_log_service import (
    OperationLogService,
)

router = APIRouter()


def _operation_log_to_out(
    log: OperationLog,
    tenant_short_name: Optional[str],
    real_name: Optional[str],
) -> dict:
    return (
        OperationLogOut.model_validate(log)
        .model_copy(
            update={
                "tenant_short_name": tenant_short_name,
                "real_name": real_name,
            }
        )
        .model_dump(by_alias=True)
    )


@router.get("/page")
async def page_operation_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    tenant_code: Optional[str] = Query(None, alias="tenantCode"),
    username: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """分页查询租户操作日志"""
    items, total = await OperationLogService.page_operation_logs(
        db,
        page=page,
        page_size=limit,
        tenant_code=tenant_code,
        username=username,
        module=module,
        action=action,
        status=status,
        start_time=createTimeStart,
        end_time=createTimeEnd,
        sort=sort,
        order=order,
    )
    return success(data={
        "list": [
            _operation_log_to_out(log, sn, rn) for log, sn, rn in items
        ],
        "count": total,
    })


@router.get("")
async def list_operation_logs(
    tenant_code: Optional[str] = Query(None, alias="tenantCode"),
    username: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """查询租户操作日志列表（不分页，用于导出）"""
    items = await OperationLogService.list_operation_logs(
        db,
        tenant_code=tenant_code,
        username=username,
        module=module,
        action=action,
        status=status,
        start_time=createTimeStart,
        end_time=createTimeEnd,
        sort=sort,
        order=order,
    )
    return success(
        data=[_operation_log_to_out(log, sn, rn) for log, sn, rn in items]
    )


@router.get("/{log_id}")
async def get_operation_log(
    log_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取操作日志详情"""
    record = await OperationLogService.get_operation_log_by_id(db, log_id)
    if not record:
        return fail("操作日志记录不存在")
    log, sn, rn = record
    return success(data=_operation_log_to_out(log, sn, rn))
