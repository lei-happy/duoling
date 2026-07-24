"""开放平台 - 接入凭证（平台库）

一个应用可签发两类凭证：
- api：AppKey(ak_) + AppSecret(sk_)，HMAC 签名鉴权，供客户系统对接
- mcp：Token(mcp_)，Bearer 鉴权，供 AI 工具接入

Secret/Token 仅存哈希，永不落明文。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, BigInteger, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class OpenCredential(PlatformModelBase):
    """接入凭证"""

    __tablename__ = "open_credential"
    __table_args__ = (
        Index("uk_open_cred_ak", "access_key", unique=True),
        Index("ix_open_cred_app", "app_id"),
        Index("ix_open_cred_tenant", "tenant_code"),
        {"comment": "开放平台接入凭证"},
    )

    app_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="所属应用 open_app.id"
    )
    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="冗余租户，便于数据面单表定位租户"
    )
    cred_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="api", comment="api / mcp"
    )
    access_key: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="AppKey(ak_) 或 MCP(mcp_) 公开标识"
    )
    secret_store: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="凭证机密：API=可解密密文（供 HMAC 校验）/ MCP=Token 哈希；永不存明文原样",
    )
    scope: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="授权能力码白名单，如 ['waybill.query']"
    )
    ip_whitelist: Mapped[str] = mapped_column(
        String(512), nullable=False, default="", server_default="",
        comment="来源 IP 白名单（逗号分隔），空=不限",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="enabled",
        server_default="enabled",
        comment="enabled 启用 / disabled 停用 / revoked 已吊销",
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="到期时间，NULL=长期有效"
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近调用时间"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 user_id"
    )
