"""调用审计服务（租户库 biz_open_call_log）

- record()：数据面每次调用后 best-effort 落库（异常降级为日志，不影响主调用）
- page_logs() / stats()：控制面「调用记录」查询
"""

from datetime import datetime, timedelta
from typing import Optional

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.modules.open_platform.models.tenant.biz_open_call_log import BizOpenCallLog


class AuditService:
    @staticmethod
    async def record(tenant_code: str, payload: dict) -> None:
        """独立事务写审计；失败只记日志，不抛出。"""
        try:
            await db_manager.ensure_tenant_tables(tenant_code, ["biz_open_call_log"])
            async for db in db_manager.get_tenant_session(tenant_code):
                db.add(BizOpenCallLog(**payload))
        except Exception as e:  # pragma: no cover - 审计不可影响主链路
            logger.warning(f"开放平台审计写入失败 tenant={tenant_code}: {e}")

    @staticmethod
    async def page_logs(
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 20,
        capability_code: Optional[str] = None,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        app_id: Optional[int] = None,
    ) -> dict:
        conds = [BizOpenCallLog.is_deleted == 0]
        if capability_code:
            conds.append(BizOpenCallLog.capability_code == capability_code)
        if status:
            conds.append(BizOpenCallLog.status == status)
        if channel:
            conds.append(BizOpenCallLog.channel == channel)
        if app_id:
            conds.append(BizOpenCallLog.app_id == app_id)

        total = await db.scalar(
            select(func.count()).select_from(BizOpenCallLog).where(*conds)
        )
        rows = (
            await db.execute(
                select(BizOpenCallLog)
                .where(*conds)
                .order_by(BizOpenCallLog.id.desc())
                .limit(limit)
                .offset((page - 1) * limit)
            )
        ).scalars().all()

        return {
            "list": [
                {
                    "id": r.id,
                    "request_id": r.request_id,
                    "app_id": r.app_id,
                    "channel": r.channel,
                    "capability_code": r.capability_code,
                    "status": r.status,
                    "error_code": r.error_code,
                    "http_status": r.http_status,
                    "latency_ms": r.latency_ms,
                    "client_ip": r.client_ip,
                    "result_summary": r.result_summary,
                    "created_at": r.created_at,
                }
                for r in rows
            ],
            "count": int(total or 0),
        }

    @staticmethod
    async def stats(db: AsyncSession, days: int = 1) -> dict:
        since = datetime.now() - timedelta(days=days)
        base = [BizOpenCallLog.is_deleted == 0, BizOpenCallLog.created_at >= since]

        total = await db.scalar(
            select(func.count()).select_from(BizOpenCallLog).where(*base)
        ) or 0
        success = await db.scalar(
            select(func.count())
            .select_from(BizOpenCallLog)
            .where(*base, BizOpenCallLog.status == "success")
        ) or 0
        avg_latency = await db.scalar(
            select(func.avg(BizOpenCallLog.latency_ms)).where(*base)
        )

        top_rows = (
            await db.execute(
                select(
                    BizOpenCallLog.capability_code,
                    func.count().label("cnt"),
                )
                .where(*base)
                .group_by(BizOpenCallLog.capability_code)
                .order_by(func.count().desc())
                .limit(5)
            )
        ).all()

        return {
            "total": int(total),
            "success": int(success),
            "successRate": round(success / total, 4) if total else 0,
            "avgLatencyMs": int(avg_latency or 0),
            "topCapabilities": [
                {"capability_code": r[0], "count": int(r[1])} for r in top_rows
            ],
        }
