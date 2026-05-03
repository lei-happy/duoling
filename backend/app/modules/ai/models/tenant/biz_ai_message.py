"""
AI 会话消息明细（租户库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Integer, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiTenantBase


class BizAiMessage(AiTenantBase):
    """AI 会话消息

    role 含义：
    - user      : 用户消息
    - assistant : 数字员工回复（可能伴随 tool_calls）
    - tool      : 工具执行结果（tool_call_id 关联到 assistant.tool_calls 的某次调用）
    - system    : 系统提示词（一般不入库，但留余地）
    """

    __tablename__ = "biz_ai_message"
    __table_args__ = (
        Index("idx_ai_msg_session", "session_id"),
        Index("idx_ai_msg_role", "role"),
        {"comment": "AI 会话消息表"},
    )

    session_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="会话ID"
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="角色 user/assistant/tool/system"
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="消息文本内容"
    )
    tool_calls: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="assistant 消息触发的工具调用列表"
    )
    tool_call_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="role=tool 时关联的 tool_call_id",
    )
    tool_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="role=tool 时的工具名"
    )
    attachments: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="附件列表（上传文件 ID + 元信息）",
    )
    model_used: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="本条消息使用的模型名"
    )
    prompt_tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="prompt token 数"
    )
    completion_tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="completion token 数"
    )
    finish_reason: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="LLM 结束原因 stop/length/tool_calls/content_filter",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        comment="状态 0-异常 1-成功 2-pending（流式生成中或等待确认）",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="错误信息"
    )
