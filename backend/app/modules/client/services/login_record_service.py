"""
客户端登录记录查询与写入

从租户库 biz_login_log 查询；写入失败不影响登录主流程。
"""

from typing import Any, List, Optional, Tuple

from loguru import logger
from sqlalchemy import select, func, and_, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.database import db_manager
from app.modules.client.models.biz_login_log import BizLoginLog
from app.modules.client.models.user.biz_user import BizUser

_LOGIN_SORT_COLUMNS = {
    "username": BizLoginLog.username,
    "nickname": BizUser.real_name,
    "ip": BizLoginLog.ip,
    "device": BizLoginLog.device,
    "os": BizLoginLog.os,
    "browser": BizLoginLog.browser,
    "loginType": BizLoginLog.login_type,
    "comments": BizLoginLog.comments,
    "createTime": BizLoginLog.created_at,
}


def _order_clauses(sort: Optional[str], order: Optional[str]) -> List[Any]:
    col = _LOGIN_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [desc(BizLoginLog.created_at), desc(BizLoginLog.id)]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    return [primary, desc(BizLoginLog.id)]


def _client_ip(request: Optional[Request]) -> Optional[str]:
    if not request or not request.client:
        return None
    return request.client.host


def _ua_browser(request: Optional[Request]) -> str:
    if not request:
        return ""
    ua = (request.headers.get("user-agent") or "").strip()
    return ua[:255] if ua else ""


class LoginRecordService:
    """登录记录"""

    @staticmethod
    async def record_login_event(
        *,
        tenant_code: str,
        username: str,
        login_type: int,
        request: Optional[Request] = None,
    ) -> None:
        """写入一条登录日志（失败仅打日志，不抛异常）"""
        try:
            await db_manager.ensure_tenant_tables(tenant_code, ["biz_login_log"])
            async for tenant_db in db_manager.get_tenant_session(tenant_code):
                r = await tenant_db.execute(
                    select(BizUser.id).where(
                        BizUser.phone == username,
                        BizUser.is_deleted == 0,
                    )
                )
                biz_uid = r.scalar_one_or_none()
                row = BizLoginLog(
                    user_id=biz_uid,
                    username=username,
                    os="",
                    device="",
                    browser=_ua_browser(request),
                    ip=_client_ip(request),
                    login_type=login_type,
                    comments="",
                )
                tenant_db.add(row)
        except Exception as e:
            logger.warning(f"写入登录日志失败 tenant={tenant_code}: {e}")

    @staticmethod
    async def page_login_logs(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        nickname: Optional[str] = None,
        login_type: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Tuple[List[Tuple[BizLoginLog, Optional[str]]], int]:
        """分页查询；返回 (日志, 昵称) 元组列表。"""
        conditions = [BizLoginLog.is_deleted == 0]

        if username:
            pattern = f"%{username}%"
            conditions.append(BizLoginLog.username.like(pattern))
        if nickname:
            pattern = f"%{nickname}%"
            conditions.append(
                or_(
                    BizUser.real_name.like(pattern),
                    BizUser.nickname.like(pattern),
                )
            )
        if login_type is not None:
            conditions.append(BizLoginLog.login_type == login_type)
        if start_time:
            conditions.append(BizLoginLog.created_at >= start_time)
        if end_time:
            conditions.append(BizLoginLog.created_at <= end_time)

        where_clause = and_(*conditions)

        count_query = (
            select(func.count(BizLoginLog.id))
            .select_from(BizLoginLog)
            .outerjoin(BizUser, BizLoginLog.user_id == BizUser.id)
            .where(where_clause)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            select(BizLoginLog, BizUser.real_name)
            .outerjoin(BizUser, BizLoginLog.user_id == BizUser.id)
            .where(where_clause)
        )
        query = query.order_by(*_order_clauses(sort, order))
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = [(row[0], row[1]) for row in result.all()]
        return items, total

    @staticmethod
    async def list_login_logs(
        db: AsyncSession,
        *,
        username: Optional[str] = None,
        nickname: Optional[str] = None,
        login_type: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[Tuple[BizLoginLog, Optional[str]]]:
        conditions = [BizLoginLog.is_deleted == 0]

        if username:
            pattern = f"%{username}%"
            conditions.append(BizLoginLog.username.like(pattern))
        if nickname:
            pattern = f"%{nickname}%"
            conditions.append(
                or_(
                    BizUser.real_name.like(pattern),
                    BizUser.nickname.like(pattern),
                )
            )
        if login_type is not None:
            conditions.append(BizLoginLog.login_type == login_type)
        if start_time:
            conditions.append(BizLoginLog.created_at >= start_time)
        if end_time:
            conditions.append(BizLoginLog.created_at <= end_time)

        where_clause = and_(*conditions)
        query = (
            select(BizLoginLog, BizUser.real_name)
            .outerjoin(BizUser, BizLoginLog.user_id == BizUser.id)
            .where(where_clause)
        )
        query = query.order_by(*_order_clauses(sort, order))
        result = await db.execute(query)
        return [(row[0], row[1]) for row in result.all()]
