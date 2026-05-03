"""调用日志与统计服务（租户库 + 平台库）"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.models.tenant.biz_ai_session import BizAiSession
from app.modules.ai.models.tenant.biz_ai_tool_call_log import BizAiToolCallLog


class AuditService:
    """调用日志查询（按租户）+ 全局统计"""

    @staticmethod
    async def page_tool_logs(
        tenant_db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        session_id: Optional[int] = None,
        tool_code: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        base = select(BizAiToolCallLog).where(BizAiToolCallLog.is_deleted == 0)
        if session_id:
            base = base.where(BizAiToolCallLog.session_id == session_id)
        if tool_code:
            base = base.where(BizAiToolCallLog.tool_code == tool_code)
        if status:
            base = base.where(BizAiToolCallLog.status == status)
        if user_id:
            base = base.where(BizAiToolCallLog.user_id == user_id)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await tenant_db.execute(count_q)).scalar() or 0
        rows = (
            await tenant_db.execute(
                base.order_by(BizAiToolCallLog.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [AuditService._tool_log_to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_tenant_stats(
        tenant_db: AsyncSession,
        days: int = 7,
    ) -> dict:
        """单租户统计概览（成功率、Top 工具、Token 总量）"""
        since = datetime.now() - timedelta(days=days)

        # 工具调用统计
        rows = (
            await tenant_db.execute(
                select(
                    BizAiToolCallLog.tool_code,
                    BizAiToolCallLog.status,
                    func.count().label("cnt"),
                    func.avg(BizAiToolCallLog.latency_ms).label("avg_latency"),
                )
                .where(
                    BizAiToolCallLog.is_deleted == 0,
                    BizAiToolCallLog.created_at >= since,
                )
                .group_by(BizAiToolCallLog.tool_code, BizAiToolCallLog.status)
            )
        ).all()
        tool_stats: dict[str, dict] = {}
        for r in rows:
            slot = tool_stats.setdefault(
                r.tool_code,
                {"tool_code": r.tool_code, "total": 0, "success": 0, "failed": 0, "denied": 0, "avg_latency_ms": 0, "_lat_sum": 0, "_lat_n": 0},
            )
            slot["total"] += int(r.cnt or 0)
            if r.status == "success":
                slot["success"] += int(r.cnt or 0)
            elif r.status == "failed":
                slot["failed"] += int(r.cnt or 0)
            elif r.status == "denied":
                slot["denied"] += int(r.cnt or 0)
            slot["_lat_sum"] += float(r.avg_latency or 0) * int(r.cnt or 0)
            slot["_lat_n"] += int(r.cnt or 0)
        for s in tool_stats.values():
            s["avg_latency_ms"] = round(s["_lat_sum"] / s["_lat_n"], 1) if s["_lat_n"] else 0
            s.pop("_lat_sum")
            s.pop("_lat_n")

        # Token 总量
        token_row = (
            await tenant_db.execute(
                sa_text(
                    "SELECT IFNULL(SUM(total_prompt_tokens),0) AS pt, "
                    "IFNULL(SUM(total_completion_tokens),0) AS ct "
                    "FROM biz_ai_session WHERE is_deleted = 0"
                )
            )
        ).first()
        return {
            "since": since.strftime("%Y-%m-%d %H:%M:%S"),
            "tool_stats": list(tool_stats.values()),
            "total_prompt_tokens": int(token_row.pt or 0) if token_row else 0,
            "total_completion_tokens": int(token_row.ct or 0) if token_row else 0,
        }

    # ============ 会话浏览 ============

    @staticmethod
    async def page_sessions(
        tenant_db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        employee_code: Optional[str] = None,
        user_id: Optional[int] = None,
        status: Optional[int] = None,
    ) -> dict:
        """分页列出某租户的所有 AI 会话（运营观测视图）"""
        base = select(BizAiSession).where(BizAiSession.is_deleted == 0)
        if keyword:
            kw = f"%{keyword}%"
            base = base.where(
                (BizAiSession.title.like(kw))
                | (BizAiSession.session_no.like(kw))
            )
        if employee_code:
            base = base.where(BizAiSession.employee_code == employee_code)
        if user_id:
            base = base.where(BizAiSession.user_id == user_id)
        if status is not None:
            base = base.where(BizAiSession.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await tenant_db.execute(count_q)).scalar() or 0
        rows = (
            await tenant_db.execute(
                base.order_by(
                    BizAiSession.last_message_at.desc(),
                    BizAiSession.id.desc(),
                )
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [AuditService._session_to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_session_messages(
        tenant_db: AsyncSession,
        session_id: int,
        limit: int = 200,
    ) -> dict:
        """列出某会话的全部消息（用于运营查看对话回放）"""
        sess = (
            await tenant_db.execute(
                select(BizAiSession).where(
                    BizAiSession.id == session_id,
                    BizAiSession.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not sess:
            return {"session": None, "messages": []}

        rows = (
            await tenant_db.execute(
                select(BizAiMessage)
                .where(
                    BizAiMessage.session_id == session_id,
                    BizAiMessage.is_deleted == 0,
                )
                .order_by(BizAiMessage.id.asc())
                .limit(limit)
            )
        ).scalars().all()
        return {
            "session": AuditService._session_to_dict(sess),
            "messages": [AuditService._message_to_dict(r) for r in rows],
        }

    @staticmethod
    def _session_to_dict(row: BizAiSession) -> dict:
        return {
            "id": row.id,
            "sessionNo": row.session_no,
            "userId": row.user_id,
            "employeeCode": row.employee_code,
            "employeeName": row.employee_name,
            "title": row.title,
            "status": row.status,
            "lastMessageAt": row.last_message_at.strftime("%Y-%m-%d %H:%M:%S")
            if row.last_message_at
            else None,
            "messageCount": row.message_count or 0,
            "totalPromptTokens": row.total_prompt_tokens or 0,
            "totalCompletionTokens": row.total_completion_tokens or 0,
            "createdAt": row.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if row.created_at
            else None,
        }

    @staticmethod
    def _message_to_dict(row: BizAiMessage) -> dict:
        return {
            "id": row.id,
            "sessionId": row.session_id,
            "role": row.role,
            "content": row.content,
            "toolCalls": row.tool_calls,
            "toolCallId": row.tool_call_id,
            "toolName": row.tool_name,
            "attachments": row.attachments,
            "modelUsed": row.model_used,
            "promptTokens": row.prompt_tokens or 0,
            "completionTokens": row.completion_tokens or 0,
            "finishReason": row.finish_reason,
            "status": row.status,
            "errorMessage": row.error_message,
            "createdAt": row.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if row.created_at
            else None,
        }

    @staticmethod
    def _tool_log_to_dict(row: BizAiToolCallLog) -> dict:
        return {
            "id": row.id,
            "sessionId": row.session_id,
            "messageId": row.message_id,
            "toolCallId": row.tool_call_id,
            "toolCode": row.tool_code,
            "toolName": row.tool_name,
            "userId": row.user_id,
            "params": row.params,
            "resultSummary": row.result_summary,
            "status": row.status,
            "errorMessage": row.error_message,
            "latencyMs": row.latency_ms,
            "createdAt": row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else None,
        }


async def fetch_tenant_codes_for_audit() -> list[str]:
    """读取所有已开通 ai_assistant 的租户编码（用于 Console 端跨租户查询）"""
    factory = db_manager._platform_session_factory  # noqa: SLF001
    if factory is None:
        return []
    async with factory() as session:
        rows = (
            await session.execute(
                sa_text(
                    """
                    SELECT DISTINCT t.tenant_code
                    FROM sys_tenant t
                    JOIN sys_tenant_product tp ON tp.tenant_id = t.id AND tp.is_deleted = 0
                    JOIN sys_product_version pv ON pv.id = tp.version_id AND pv.is_deleted = 0
                    JOIN sys_version_feature vf ON vf.version_id = pv.id
                        AND vf.is_deleted = 0 AND vf.status = 1
                    JOIN sys_product_feature pf ON pf.id = vf.feature_id
                        AND pf.is_deleted = 0 AND pf.feature_code = 'ai_assistant'
                    WHERE t.is_deleted = 0
                    """
                )
            )
        ).fetchall()
    return [r[0] for r in rows if r and r[0]]
