"""
操作日志查询服务（日志中心）

从平台库 sys_operation_log 查询租户端的操作日志；
关联 sys_tenant：列表展示优先 short_name，空则回退 tenant_name；
操作用户姓名：JWT 中 user_id 为平台 sys_user.id，与租户库 biz_user.id 不一致，
@operation_log 写入的 username 为登录手机号，故按 biz_user.phone 批量关联 real_name，
无手机号时再回退按 biz_user.id 查询（兼容历史或特殊数据）。
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


def _tenant_list_label(
    short_name: Optional[str], tenant_name: Optional[str]
) -> Optional[str]:
    s = (short_name or "").strip()
    if s:
        return s
    t = (tenant_name or "").strip()
    return t or None


async def _batch_real_names_by_phone(
    logs: List[OperationLog],
) -> Dict[Tuple[str, str], Optional[str]]:
    """按租户用手机号批量查 biz_user.real_name（与装饰器写入的 username 一致）。"""
    by_tenant: dict[str, set[str]] = defaultdict(set)
    for log in logs:
        if log.tenant_code and log.username:
            p = str(log.username).strip()
            if p:
                by_tenant[log.tenant_code].add(p)

    out: Dict[Tuple[str, str], Optional[str]] = {}
    for tcode, phones in by_tenant.items():
        if not phones:
            continue
        try:
            db_manager._get_or_create_tenant_engine(tcode)
            factory = db_manager._tenant_session_factories.get(tcode)
            if not factory:
                continue
            async with factory() as session:
                stmt = select(BizUser.phone, BizUser.real_name).where(
                    BizUser.phone.in_(list(phones))
                )
                result = await session.execute(stmt)
                for phone, rn in result.all():
                    out[(tcode, str(phone).strip())] = rn
        except Exception as e:
            logger.warning(
                f"操作日志按手机号关联租户用户姓名失败 tenant={tcode}: {e}"
            )
    return out


async def _batch_real_names_by_biz_id(
    logs: List[OperationLog],
) -> Dict[Tuple[str, int], Optional[str]]:
    """按 biz_user.id 批量查询 real_name（次要路径，兼容 user_id 已为租户主键的数据）。"""
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
            logger.warning(
                f"操作日志按用户ID关联租户用户姓名失败 tenant={tcode}: {e}"
            )
    return out


def _resolve_operator_real_name(
    log: OperationLog,
    phone_map: Dict[Tuple[str, str], Optional[str]],
    id_map: Dict[Tuple[str, int], Optional[str]],
) -> Optional[str]:
    if log.tenant_code and log.username:
        p = str(log.username).strip()
        if p and (log.tenant_code, p) in phone_map:
            return phone_map[(log.tenant_code, p)]
    if log.tenant_code and log.user_id is not None:
        return id_map.get((log.tenant_code, int(log.user_id)))
    return None


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
        """分页查询；返回 (日志, 租户展示名, 操作人真实姓名) 元组列表。"""
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
            select(OperationLog, Tenant.short_name, Tenant.tenant_name)
            .outerjoin(Tenant, _TENANT_JOIN)
            .where(where_clause)
            .order_by(*_order_clauses(sort, order))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        rows = [(r[0], r[1], r[2]) for r in result.all()]
        logs = [r[0] for r in rows]
        phone_map = await _batch_real_names_by_phone(logs)
        id_map = await _batch_real_names_by_biz_id(logs)

        triples: List[Tuple[OperationLog, Optional[str], Optional[str]]] = []
        for log, short_name, tenant_name in rows:
            label = _tenant_list_label(short_name, tenant_name)
            rn = _resolve_operator_real_name(log, phone_map, id_map)
            triples.append((log, label, rn))

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
            select(OperationLog, Tenant.short_name, Tenant.tenant_name)
            .outerjoin(Tenant, _TENANT_JOIN)
            .where(where_clause)
            .order_by(*_order_clauses(sort, order))
        )
        result = await db.execute(query)
        rows = [(r[0], r[1], r[2]) for r in result.all()]
        logs = [r[0] for r in rows]
        phone_map = await _batch_real_names_by_phone(logs)
        id_map = await _batch_real_names_by_biz_id(logs)

        triples: List[Tuple[OperationLog, Optional[str], Optional[str]]] = []
        for log, short_name, tenant_name in rows:
            label = _tenant_list_label(short_name, tenant_name)
            rn = _resolve_operator_real_name(log, phone_map, id_map)
            triples.append((log, label, rn))
        return triples

    @staticmethod
    async def get_operation_log_by_id(
        db: AsyncSession, log_id: int
    ) -> Optional[Tuple[OperationLog, Optional[str], Optional[str]]]:
        """根据 ID 获取详情：(日志, 租户展示名, 操作人真实姓名)。"""
        stmt = (
            select(OperationLog, Tenant.short_name, Tenant.tenant_name)
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
        log, short_name, tenant_name = row[0], row[1], row[2]
        phone_map = await _batch_real_names_by_phone([log])
        id_map = await _batch_real_names_by_biz_id([log])
        label = _tenant_list_label(short_name, tenant_name)
        rn = _resolve_operator_real_name(log, phone_map, id_map)
        return log, label, rn
