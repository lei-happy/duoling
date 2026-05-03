"""
AI 会话/用户上下文记忆 KV（租户库）
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, BigInteger, JSON, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiTenantBase


class BizAiContext(AiTenantBase):
    """会话/用户上下文记忆 KV

    scope 取值：
    - session : 会话级（仅本次会话有效）
    - user    : 用户级（跨会话，仅本用户）
    - global  : 租户级全局（远期）
    """

    __tablename__ = "biz_ai_context"
    __table_args__ = (
        UniqueConstraint("session_id", "scope", "key", name="uk_ai_ctx"),
        Index("idx_ai_ctx_scope_key", "scope", "key"),
        {"comment": "AI 上下文记忆表"},
    )

    session_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="会话ID（user/global scope 时可为空）"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="用户ID（user scope 必填）"
    )
    scope: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="作用域 session/user/global"
    )
    key: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="键"
    )
    value: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="值（JSON）"
    )
    expire_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="过期时间（NULL 表示不过期）"
    )
