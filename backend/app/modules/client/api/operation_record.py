"""
客户端操作记录查询接口

供企业端查看本租户的操作日志
"""

from typing import Optional, Tuple, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.models.biz_operation_log import BizOperationLog
from app.modules.client.schemas.operation_record import BizOperationLogOut
from app.modules.client.services.operation_record_service import (
    BizOperationLogService,
)

router = APIRouter()


def _operation_log_rows_to_out(
    rows: List[Tuple[BizOperationLog, Optional[str]]],
) -> list:
    out: list = []
    for log, real_name in rows:
        item = BizOperationLogOut.model_validate(log).model_copy(
            update={"real_name": real_name}
        )
        out.append(item.model_dump(by_alias=True))
    return out


@router.get("/page")
async def page_operation_records(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    username: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询操作日志"""
    items, total = await BizOperationLogService.page_operation_logs(
        db,
        page=page,
        page_size=limit,
        username=username,
        module=module,
        status=status,
        start_time=createTimeStart,
        end_time=createTimeEnd,
        sort=sort,
        order=order,
    )
    return success(data={
        "list": _operation_log_rows_to_out(items),
        "count": total,
    })


@router.get("")
async def list_operation_records(
    username: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """查询操作日志列表（不分页，用于导出）"""
    items = await BizOperationLogService.list_operation_logs(
        db,
        username=username,
        module=module,
        status=status,
        start_time=createTimeStart,
        end_time=createTimeEnd,
        sort=sort,
        order=order,
    )
    return success(data=_operation_log_rows_to_out(items))
