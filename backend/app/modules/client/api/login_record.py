"""
客户端登录记录查询接口
"""

from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_tenant_db,
    get_current_user,
    ensure_biz_login_log_table,
)
from app.common.response import success
from app.modules.client.models.biz_login_log import BizLoginLog
from app.modules.client.schemas.login_record import BizLoginLogOut
from app.modules.client.services.login_record_service import LoginRecordService

router = APIRouter()


def _rows_to_out(
    rows: List[Tuple[BizLoginLog, Optional[str]]],
) -> list:
    out: list = []
    for log, real_name in rows:
        item = BizLoginLogOut(
            id=log.id,
            user_id=log.user_id,
            username=log.username,
            nickname=real_name,
            os=log.os or "",
            device=log.device or "",
            browser=log.browser or "",
            ip=log.ip,
            login_type=log.login_type,
            comments=log.comments,
            createTime=log.created_at,
        )
        out.append(item.model_dump(by_alias=True))
    return out


@router.get("/page")
async def page_login_records(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    username: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    loginType: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    _: None = Depends(ensure_biz_login_log_table),
    db: AsyncSession = Depends(get_tenant_db),
    __=Depends(get_current_user),
):
    """分页查询登录日志"""
    items, total = await LoginRecordService.page_login_logs(
        db,
        page=page,
        page_size=limit,
        username=username,
        nickname=nickname,
        login_type=loginType,
        start_time=createTimeStart,
        end_time=createTimeEnd,
        sort=sort,
        order=order,
    )
    return success(data={
        "list": _rows_to_out(items),
        "count": total,
    })


@router.get("")
async def list_login_records(
    username: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    loginType: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    _: None = Depends(ensure_biz_login_log_table),
    db: AsyncSession = Depends(get_tenant_db),
    __=Depends(get_current_user),
):
    """查询登录日志列表（不分页，用于导出）"""
    items = await LoginRecordService.list_login_logs(
        db,
        username=username,
        nickname=nickname,
        login_type=loginType,
        start_time=createTimeStart,
        end_time=createTimeEnd,
        sort=sort,
        order=order,
    )
    return success(data=_rows_to_out(items))
