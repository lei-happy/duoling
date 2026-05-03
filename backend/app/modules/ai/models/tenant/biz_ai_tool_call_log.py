"""
AI 工具调用日志（租户库，细粒度审计）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Integer, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiTenantBase


class BizAiToolCallLog(AiTenantBase):
    """工具调用日志（每次工具被尝试调用都记一行）"""

    __tablename__ = "biz_ai_tool_call_log"
    __table_args__ = (
        Index("idx_ai_tcl_session", "session_id"),
        Index("idx_ai_tcl_message", "message_id"),
        Index("idx_ai_tcl_tool", "tool_code"),
        Index("idx_ai_tcl_status", "status"),
        Index("idx_ai_tcl_user", "user_id"),
        {"comment": "AI 工具调用日志表"},
    )

    session_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="会话ID"
    )
    message_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="对应的 assistant 消息ID（触发本次调用的）",
    )
    tool_call_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="LLM 侧的 tool_call_id"
    )
    tool_code: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="工具编码"
    )
    tool_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="工具名称（冗余便于审计阅读）"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="发起会话的用户ID"
    )
    params: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="调用参数（脱敏后）"
    )
    result_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="结果摘要（截断+脱敏）"
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="success",
        comment="状态 success/failed/denied/pending_confirm/cancelled",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="错误信息"
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer, default=0, comment="工具执行耗时（毫秒）"
    )
    confirm_token: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="待确认状态下的 token，用户在前端确认后回传",
    )
