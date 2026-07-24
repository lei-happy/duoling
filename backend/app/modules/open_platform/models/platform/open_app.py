"""开放平台 - 接入应用（平台库）

一个接入应用 = 租户要对接的一个外部系统或 AI 工具。凭证挂在应用下。
"""

from typing import Optional

from sqlalchemy import String, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class OpenApp(PlatformModelBase):
    """接入应用"""

    __tablename__ = "open_app"
    __table_args__ = (
        Index("ix_open_app_tenant", "tenant_code"),
        {"comment": "开放平台接入应用"},
    )

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="所属租户"
    )
    name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="应用名称（用户填，如“我们的 ERP”）"
    )
    description: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", server_default="", comment="用途备注"
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="enabled",
        server_default="enabled",
        comment="enabled 启用 / disabled 停用",
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 user_id"
    )
