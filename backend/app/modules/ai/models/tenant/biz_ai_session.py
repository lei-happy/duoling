"""
AI 会话主表（租户库）
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiTenantBase


class BizAiSession(AiTenantBase):
    """AI 数字员工会话"""

    __tablename__ = "biz_ai_session"
    __table_args__ = (
        Index("idx_ai_sess_user", "user_id"),
        Index("idx_ai_sess_employee", "employee_code"),
        Index("idx_ai_sess_status", "status"),
        {"comment": "AI 会话主表"},
    )

    session_no: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="会话号"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="用户ID"
    )
    employee_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="数字员工编码"
    )
    employee_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="数字员工名称（冗余便于展示）"
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="会话标题（首条用户消息摘要）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        comment="状态 0-已关闭 1-活跃 2-归档",
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后一条消息时间"
    )
    message_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="消息数（含 user/assistant/tool 全部）"
    )
    total_prompt_tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="累计 prompt token"
    )
    total_completion_tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="累计 completion token"
    )
