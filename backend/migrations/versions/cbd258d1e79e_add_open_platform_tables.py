"""add open_platform tables

Revision ID: cbd258d1e79e
Revises: 42102ef9acac
Create Date: 2026-07-24 21:06:28.754985

说明：本迁移仅新增开放平台 4 张平台库表（open_app / open_credential /
open_mcp_config / open_capability）。autogen 因平台库 _ci 与 ORM 间存在历史 drift
夹带了大量无关 alter_column，已人工剔除，只保留本次相关的建表语句。

线上/本地首次启动时 app.core.events._bootstrap_open_platform 也会自动补建这些表
（与 ai_* 表一致），故建表使用 checkfirst 语义，重复执行安全。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "cbd258d1e79e"
down_revision: Union[str, None] = "42102ef9acac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing = set(insp.get_table_names())

    if "open_app" not in existing:
        op.create_table(
            "open_app",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="主键ID"),
            sa.Column("tenant_code", sa.String(length=32), nullable=False, comment="所属租户"),
            sa.Column("name", sa.String(length=64), nullable=False, comment="应用名称"),
            sa.Column("description", sa.String(length=255), server_default="", nullable=False, comment="用途备注"),
            sa.Column("status", sa.String(length=16), server_default="enabled", nullable=False, comment="enabled/disabled"),
            sa.Column("created_by", sa.BigInteger(), nullable=True, comment="创建人 user_id"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("is_deleted", sa.SmallInteger(), server_default="0", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            comment="开放平台接入应用",
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
            mysql_collate="utf8mb4_unicode_ci",
        )
        op.create_index("ix_open_app_tenant", "open_app", ["tenant_code"])

    if "open_credential" not in existing:
        op.create_table(
            "open_credential",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="主键ID"),
            sa.Column("app_id", sa.BigInteger(), nullable=False, comment="所属应用 open_app.id"),
            sa.Column("tenant_code", sa.String(length=32), nullable=False, comment="冗余租户"),
            sa.Column("cred_type", sa.String(length=16), nullable=False, comment="api / mcp"),
            sa.Column("access_key", sa.String(length=64), nullable=False, comment="公开标识"),
            sa.Column("secret_store", sa.String(length=256), nullable=False, comment="API=密文/MCP=哈希"),
            sa.Column("scope", sa.JSON(), nullable=True, comment="授权能力码白名单"),
            sa.Column("ip_whitelist", sa.String(length=512), server_default="", nullable=False, comment="IP 白名单"),
            sa.Column("status", sa.String(length=16), server_default="enabled", nullable=False, comment="enabled/disabled/revoked"),
            sa.Column("expires_at", sa.DateTime(), nullable=True, comment="到期时间"),
            sa.Column("last_used_at", sa.DateTime(), nullable=True, comment="最近调用"),
            sa.Column("created_by", sa.BigInteger(), nullable=True, comment="创建人"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("is_deleted", sa.SmallInteger(), server_default="0", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            comment="开放平台接入凭证",
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
            mysql_collate="utf8mb4_unicode_ci",
        )
        op.create_index("uk_open_cred_ak", "open_credential", ["access_key"], unique=True)
        op.create_index("ix_open_cred_app", "open_credential", ["app_id"])
        op.create_index("ix_open_cred_tenant", "open_credential", ["tenant_code"])

    if "open_mcp_config" not in existing:
        op.create_table(
            "open_mcp_config",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="主键ID"),
            sa.Column("app_id", sa.BigInteger(), nullable=False, comment="所属应用"),
            sa.Column("tenant_code", sa.String(length=32), nullable=False, comment="冗余租户"),
            sa.Column("credential_id", sa.BigInteger(), nullable=False, comment="绑定 MCP 凭证"),
            sa.Column("server_slug", sa.String(length=32), nullable=False, comment="URL 片段（唯一）"),
            sa.Column("display_name", sa.String(length=64), nullable=False, comment="连接名称"),
            sa.Column("enabled_capabilities", sa.JSON(), nullable=True, comment="暴露能力码"),
            sa.Column("status", sa.String(length=16), server_default="enabled", nullable=False, comment="enabled/disabled"),
            sa.Column("created_by", sa.BigInteger(), nullable=True, comment="创建人"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("is_deleted", sa.SmallInteger(), server_default="0", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            comment="开放平台 MCP 配置",
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
            mysql_collate="utf8mb4_unicode_ci",
        )
        op.create_index("uk_open_mcp_slug", "open_mcp_config", ["server_slug"], unique=True)
        op.create_index("ix_open_mcp_app", "open_mcp_config", ["app_id"])
        op.create_index("ix_open_mcp_tenant", "open_mcp_config", ["tenant_code"])

    if "open_capability" not in existing:
        op.create_table(
            "open_capability",
            sa.Column("code", sa.String(length=64), nullable=False, comment="能力码"),
            sa.Column("name", sa.String(length=64), nullable=False, comment="业务名称"),
            sa.Column("category", sa.String(length=32), server_default="", nullable=False, comment="分类"),
            sa.Column("description", sa.String(length=512), server_default="", nullable=False, comment="说明"),
            sa.Column("channels", sa.JSON(), nullable=True, comment="支持通道"),
            sa.Column("read_only", sa.SmallInteger(), server_default="1", nullable=False, comment="是否只读"),
            sa.Column("input_schema", sa.JSON(), nullable=True, comment="入参 Schema"),
            sa.Column("output_fields", sa.JSON(), nullable=True, comment="可见字段"),
            sa.Column("sensitive_fields", sa.JSON(), nullable=True, comment="脱敏字段"),
            sa.Column("risk_level", sa.String(length=16), server_default="low", nullable=False, comment="low/high"),
            sa.Column("stability", sa.String(length=16), server_default="stable", nullable=False, comment="beta/stable/deprecated/offline"),
            sa.Column("version", sa.String(length=8), server_default="v1", nullable=False, comment="契约版本"),
            sa.Column("status", sa.String(length=16), server_default="enabled", nullable=False, comment="enabled/disabled"),
            sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False, comment="展示排序"),
            sa.PrimaryKeyConstraint("code"),
            comment="开放平台能力目录",
            mysql_engine="InnoDB",
            mysql_charset="utf8mb4",
            mysql_collate="utf8mb4_unicode_ci",
        )
        op.create_index("ix_open_cap_category", "open_capability", ["category"])
        op.create_index("ix_open_cap_status", "open_capability", ["status"])


def downgrade() -> None:
    op.drop_table("open_mcp_config")
    op.drop_table("open_capability")
    op.drop_table("open_credential")
    op.drop_table("open_app")
