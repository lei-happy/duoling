"""
ContextManager: 会话上下文加载与裁剪

职责：
1) 加载历史消息（按 session_id 倒序拉最近 N 条，再正序排）
2) 把 DB 消息转成 ChatMessage 给 LLM
3) 简单滑动窗口裁剪（V1 不接 token 计数，按条数限制；后续接 tiktoken）
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.llm.base import ChatMessage, ToolCall
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.tools.registry import encode_tool_name


class ContextManager:
    @staticmethod
    async def load_history_messages(
        tenant_db: AsyncSession,
        session_id: int,
        max_messages: int = 20,
        exclude_system: bool = True,
    ) -> list[ChatMessage]:
        """加载历史消息（按时间正序）"""
        stmt = (
            select(BizAiMessage)
            .where(
                BizAiMessage.session_id == session_id,
                BizAiMessage.is_deleted == 0,
            )
            .order_by(BizAiMessage.id.desc())
            .limit(max_messages)
        )
        rows = (await tenant_db.execute(stmt)).scalars().all()
        rows = list(reversed(rows))

        messages: list[ChatMessage] = []
        for row in rows:
            if exclude_system and row.role == "system":
                continue
            messages.append(ContextManager._row_to_message(row))
        return messages

    @staticmethod
    def _row_to_message(row: BizAiMessage) -> ChatMessage:
        tool_calls: list[ToolCall] = []
        if row.tool_calls:
            for tc in row.tool_calls:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function") or {}
                raw_name = tc.get("name") or fn.get("name") or ""
                # 历史数据可能保存的是带点号的业务 code；
                # 给 LLM 时统一编码成 wire 名（encode 是幂等的，已编码不会被二次处理）
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id") or "",
                        name=encode_tool_name(raw_name),
                        arguments=tc.get("arguments") or fn.get("arguments") or "{}",
                    )
                )
        return ChatMessage(
            role=row.role,
            content=row.content,
            tool_calls=tool_calls,
            tool_call_id=row.tool_call_id,
            # tool 消息的 name 同样编码，确保和 assistant.tool_calls 的 wire 名一致
            name=encode_tool_name(row.tool_name) if row.role == "tool" and row.tool_name else None,
        )
