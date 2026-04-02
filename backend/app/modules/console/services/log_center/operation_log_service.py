"""
操作日志查询服务（日志中心）

从平台库 sys_operation_log 查询租户端的操作日志；
关联 sys_tenant.short_name；按租户库 biz_user 补全真实姓名。
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.modules.client.models.user.biz_user import BizUser
from app.modules.console.models.common.operation_log import OperationLog
from app.modules.console.models.tenant.tenant import Tenant

# 与前端表格列 prop（camelCase）对齐
_OPERATION_LOG_SORT_COLUMNS = {
    "tenantCode": OperationLog.tenant_code,
    "username": OperationLog.username,
    "module": OperationLog.module,
    "action": OperationLog.action,
    "description": OperationLog.description,
    "requestUrl": OperationLog.request_url,
    "requestMethod": OperationLog.request_method,
    "status": OperationLog.status,
    "elapsedTime": OperationLog.elapsed_time,
    "createdAt": OperationLog.created_at,
}


def _order_clauses(sort: Optional[str], order: Optional[str]) -> List[Any]:
    col = _OPERATION_LOG_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [desc(OperationLog.created_at), desc(OperationLog.id)]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    return [primary, desc(OperationLog.id)]


_TENANT_JOIN = and_(
    OperationLog.tenant_code == Tenant.tenant_code,
    Tenant.is_deleted == 0,
)


async def _batch_real_names(logs: List[OperationLog]) -> Dict[Tuple[str, int], Optional[str]]:
    """按租户批量查询 biz_user.real_name（user_id 为租户内用户主键）。"""
    by_tenant: dict[str, set[int]] = defaultdict(set)
    for log in logs:
        if log.tenant_code and log.user_id is not None:
            by_tenant[log.tenant_code].add(int(log.user_id))

    out: Dict[Tuple[str, int], Optional[str]] = {}
    for tcode, ids in by_tenant.items():
        if not ids:
            continue
        try:
            db_manager._get_or_create_tenant_engine(tcode)
            factory = db_manager._tenant_session_factories.get(tcode)
            if not factory:
                continue
            async with factory() as session:
                stmt = select(BizUser.id, BizUser.real_name).where(
                    BizUser.id.in_(list(ids))
                )
                result = await session.execute(stmt)
                for uid, rn in result.all():
                    out[(tcode, int(uid))] = rn
        except Exception as e:
            logger.warning(f"操作日志关联租户用户姓名失败 tenant={tcode}: {e}")
    return out


class OperationLogService:
    """操作日志查询服务"""

    @staticmethod
    async def page_operation_logs(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        tenant_code: Optional[str] = None,
        username: Optional[str] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Tuple[List[Tuple[OperationLog, Optional[str], Optional[str]]], int]:
        """分页查询；返回 (日志, 租户简称, 真实姓名) 元组列表。"""
        conditions = [OperationLog.is_deleted == 0]

        if tenant_code and str(tenant_code).strip():
            tc = str(tenant_code).strip()
            conditions.append(
                OperationLog.tenant_code.in_(
                    select(Tenant.tenant_code).where(
                        Tenant.is_deleted == 0,
                        or_(
                            Tenant.tenant_code == tc,
                            Tenant.short_name.like(f"%{tc}%"),
                        ),
                    )
                )
            )
        if username:
            conditions.append(OperationLog.username.like(f"%{username}%"))
        if module:
            conditions.append(OperationLog.module.like(f"%{module}%"))
        if action:
            conditions.append(OperationLog.action == action)
        if status is not None:
            conditions.append(OperationLog.status == status)
        if start_time:
            conditions.append(OperationLog.created_at >= start_time)
        if end_time:
            conditions.append(OperationLog.created_at <= end_time)

        where_clause = and_(*conditions)

        count_query = (
            select(func.count(OperationLog.id))
            .select_from(OperationLog)
            .where(where_clause)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            select(OperationLog, Tenant.short_name)
            .outerjoin(Tenant, _TENANT_JOIN)
            .where(where_clause)
            .order_by(*_order_clauses(sort, order))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        rows = [(r[0], r[1]) for r in result.all()]
        logs = [r[0] for r in rows]
        real_map = await _batch_real_names(logs)

        triples: List[Tuple[OperationLog, Optional[str], Optional[str]]] = []
        for log, short_name in rows:
            rn = None
            if log.tenant_code and log.user_id is not None:
                rn = real_map.get((log.tenant_code, int(log.user_id)))
            triples.append((log, short_name, rn))

        return triples, total

    @staticmethod
    async def list_operation_logs(
        db: AsyncSession,
        *,
        tenant_code: Optional[str] = None,
        username: Optional[str] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[Tuple[OperationLog, Optional[str], Optional[str]]]:
        """列表（不分页），结构同分页。"""
        conditions = [OperationLog.is_deleted == 0]

        if tenant_code and str(tenant_code).strip():
            tc = str(tenant_code).strip()
            conditions.append(
                OperationLog.tenant_code.in_(
                    select(Tenant.tenant_code).where(
                        Tenant.is_deleted == 0,
                        or_(
                            Tenant.tenant_code == tc,
                            Tenant.short_name.like(f"%{tc}%"),
                        ),
                    )
                )
            )
        if username:
            conditions.append(OperationLog.username.like(f"%{username}%"))
        if module:
            conditions.append(OperationLog.module.like(f"%{module}%"))
        if action:
            conditions.append(OperationLog.action == action)
        if status is not None:
            conditions.append(OperationLog.status == status)
        if start_time:
            conditions.append(OperationLog.created_at >= start_time)
        if end_time:
            conditions.append(OperationLog.created_at <= end_time)

        where_clause = and_(*conditions)
        query = (
            select(OperationLog, Tenant.short_name)
            .outerjoin(Tenant, _TENANT_JOIN)
            .where(where_clause)
            .order_by(*_order_clauses(sort, order))
        )
        result = await db.execute(query)
        rows = [(r[0], r[1]) for r in result.all()]
        logs = [r[0] for r in rows]
        real_map = await _batch_real_names(logs)

        triples: List[Tuple[OperationLog, Optional[str], Optional[str]]] = []
        for log, short_name in rows:
            rn = None
            if log.tenant_code and log.user_id is not None:
                rn = real_map.get((log.tenant_code, int(log.user_id)))
            triples.append((log, short_name, rn))
        return triples

    @staticmethod
    async def get_operation_log_by_id(
        db: AsyncSession, log_id: int
    ) -> Optional[Tuple[OperationLog, Optional[str], Optional[str]]]:
        """根据 ID 获取详情：(日志, 租户简称, 真实姓名)。"""
        stmt = (
            select(OperationLog, Tenant.short_name)
            .outerjoin(Tenant, _TENANT_JOIN)
            .where(
                OperationLog.id == log_id,
                OperationLog.is_deleted == 0,
            )
        )
        result = await db.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        log, short_name = row[0], row[1]
        real_map = await _batch_real_names([log])
        rn = None
        if log.tenant_code and log.user_id is not None:
            rn = real_map.get((log.tenant_code, int(log.user_id)))
        return log, short_name, rn
