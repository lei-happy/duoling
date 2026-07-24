"""开放平台 - MCP 配置（平台库）

一条 MCP 配置 = 一个可被 AI 工具连接的远程 MCP Server 端点。
display_name 与 server_slug 分离：改名不影响连接（url/token 不变）。
"""

from typing import Optional

from sqlalchemy import String, BigInteger, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class OpenMcpConfig(PlatformModelBase):
    """MCP 配置"""

    __tablename__ = "open_mcp_config"
    __table_args__ = (
        Index("uk_open_mcp_slug", "server_slug", unique=True),
        Index("ix_open_mcp_app", "app_id"),
        Index("ix_open_mcp_tenant", "tenant_code"),
        {"comment": "开放平台 MCP 配置"},
    )

    app_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="所属应用 open_app.id"
    )
    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="冗余租户，便于数据面定位"
    )
    credential_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="绑定的 MCP 凭证 open_credential.id"
    )
    server_slug: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="URL 路径片段（唯一），如 7f3a9c2e"
    )
    display_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="用户自定义连接名称（可改，不影响连接）"
    )
    enabled_capabilities: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="暴露为 MCP Tool 的能力码"
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
