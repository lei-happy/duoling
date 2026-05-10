"""
企业最新动态（租户库）

协作可见的业务事件摘要，与 biz_operation_log 审计日志分工不同。
"""

from typing import Any, Dict, Optional

from datetime import datetime

from sqlalchemy import String, BigInteger, Text, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizCompanyActivity(TenantModelBase):
    """企业动态事件"""

    __tablename__ = "biz_company_activity"
    __table_args__ = {"comment": "企业最新动态（协作可见）"}
    __table_tier__ = "business"

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="事件发生时间",
    )
    actor_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 biz_user.id"
    )
    actor_display_name: Mapped[Optional[str]] = mapped_column(
        String(80), nullable=True, comment="操作人展示名快照"
    )
    event_code: Mapped[str] = mapped_column(
        String(80), nullable=False, comment="事件编码，如 capacity.self_bind"
    )
    summary: Mapped[str] = mapped_column(
        Text, nullable=False, comment="可直接展示的中文摘要"
    )
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="结构化扩展字段"
    )
