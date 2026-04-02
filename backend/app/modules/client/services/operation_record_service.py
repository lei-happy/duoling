"""
客户端操作记录查询服务

从租户库 biz_operation_log 查询当前租户的操作日志
"""

from typing import Any, List, Optional, Tuple

from sqlalchemy import select, func, and_, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.biz_operation_log import BizOperationLog
from app.modules.client.models.user.biz_user import BizUser

# 与前端表格列 prop（camelCase）对齐，仅白名单参与排序
_OPERATION_LOG_SORT_COLUMNS = {
    "username": BizOperationLog.username,
    "module": BizOperationLog.module,
    "action": BizOperationLog.action,
    "description": BizOperationLog.description,
    "requestUrl": BizOperationLog.request_url,
    "requestMethod": BizOperationLog.request_method,
    "status": BizOperationLog.status,
    "elapsedTime": BizOperationLog.elapsed_time,
    "createdAt": BizOperationLog.created_at,
}


def _operation_log_order_clauses(
    sort: Optional[str], order: Optional[str]
) -> List[Any]:
    """解析排序；非法或未传时按操作时间降序（与列表默认一致）。"""
    col = _OPERATION_LOG_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [desc(BizOperationLog.created_at), desc(BizOperationLog.id)]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    # 稳定次序：同字段值时按主键降序
    return [primary, desc(BizOperationLog.id)]


class BizOperationLogService:
    """操作记录查询服务"""

    @staticmethod
    async def page_operation_logs(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        module: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Tuple[List[BizOperationLog], int]:
        """分页查询操作日志"""
        conditions = [BizOperationLog.is_deleted == 0]

        if username:
            pattern = f"%{username}%"
            conditions.append(
                or_(
                    BizOperationLog.username.like(pattern),
                    BizUser.real_name.like(pattern),
                    BizUser.phone.like(pattern),
                )
            )
        if module:
            conditions.append(BizOperationLog.module.like(f"%{module}%"))
        if status is not None:
            conditions.append(BizOperationLog.status == status)
        if start_time:
            conditions.append(BizOperationLog.created_at >= start_time)
        if end_time:
            conditions.append(BizOperationLog.created_at <= end_time)

        where_clause = and_(*conditions)

        count_query = (
            select(func.count(BizOperationLog.id))
            .select_from(BizOperationLog)
            .outerjoin(BizUser, BizOperationLog.user_id == BizUser.id)
            .where(where_clause)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            select(BizOperationLog, BizUser.real_name)
            .outerjoin(BizUser, BizOperationLog.user_id == BizUser.id)
            .where(where_clause)
        )

        query = query.order_by(*_operation_log_order_clauses(sort, order))

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = [(row[0], row[1]) for row in result.all()]

        return items, total

    @staticmethod
    async def list_operation_logs(
        db: AsyncSession,
        *,
        username: Optional[str] = None,
        module: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[BizOperationLog]:
        """查询操作日志列表（不分页，用于导出）"""
        conditions = [BizOperationLog.is_deleted == 0]

        if username:
            pattern = f"%{username}%"
            conditions.append(
                or_(
                    BizOperationLog.username.like(pattern),
                    BizUser.real_name.like(pattern),
                    BizUser.phone.like(pattern),
                )
            )
        if module:
            conditions.append(BizOperationLog.module.like(f"%{module}%"))
        if status is not None:
            conditions.append(BizOperationLog.status == status)
        if start_time:
            conditions.append(BizOperationLog.created_at >= start_time)
        if end_time:
            conditions.append(BizOperationLog.created_at <= end_time)

        where_clause = and_(*conditions)
        query = (
            select(BizOperationLog, BizUser.real_name)
            .outerjoin(BizUser, BizOperationLog.user_id == BizUser.id)
            .where(where_clause)
        )

        query = query.order_by(*_operation_log_order_clauses(sort, order))

        result = await db.execute(query)
        return [(row[0], row[1]) for row in result.all()]
