"""开放平台 - 调用审计（租户库）

高频、租户可查、随租户物理隔离。每次对外调用（含被拒/失败）留痕。
"""

from typing import Optional

from sqlalchemy import String, BigInteger, Integer, SmallInteger, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizOpenCallLog(TenantModelBase):
    """开放平台调用审计"""

    __tablename__ = "biz_open_call_log"
    __table_tier__ = "business"
    __table_args__ = (
        Index("ix_ocl_created", "created_at"),
        Index("ix_ocl_app", "app_id"),
        Index("ix_ocl_cap", "capability_code"),
        Index("ix_ocl_status", "status"),
        Index("ix_ocl_reqid", "request_id"),
        {"comment": "开放平台调用审计"},
    )

    request_id: Mapped[str] = mapped_column(
        String(48), nullable=False, comment="全局请求号"
    )
    app_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="调用方应用 open_app.id"
    )
    credential_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="调用方凭证 open_credential.id"
    )
    channel: Mapped[str] = mapped_column(
        String(8), nullable=False, default="api", comment="api / mcp"
    )
    capability_code: Mapped[str] = mapped_column(
        String(64), nullable=False, default="", server_default="", comment="能力码"
    )
    method: Mapped[str] = mapped_column(
        String(8), nullable=False, default="", server_default="", comment="HTTP 方法"
    )
    path: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", server_default="", comment="请求路径"
    )
    params_masked: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="脱敏入参"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="success",
        comment="success / failed / denied",
    )
    error_code: Mapped[str] = mapped_column(
        String(32), nullable=False, default="", server_default="", comment="错误码"
    )
    http_status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="HTTP 状态码"
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="耗时毫秒"
    )
    client_ip: Mapped[str] = mapped_column(
        String(64), nullable=False, default="", server_default="", comment="来源 IP"
    )
    user_agent: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", server_default="", comment="UA"
    )
    result_summary: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", server_default="", comment="结果摘要"
    )
