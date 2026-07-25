"""add sys_sensitive_word

Revision ID: a1c4e7b2f083
Revises: dab0f20fa617
Create Date: 2026-07-25 18:20:00.000000

说明：新增平台级敏感词库表 sys_sensitive_word，由运营后台维护。
首个消费方是服务平台挂牌发布预检（04.运营审核与风控设计.md §2.3）。

本迁移手写而非 autogenerate：本地开发库存在历史 drift，autogen 会夹带大量
无关且具破坏性的语句（先例见 dab0f20fa617）。本次只建一张表，手写更安全。

建表使用存在性守卫，重复执行安全。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1c4e7b2f083"
down_revision: Union[str, None] = "dab0f20fa617"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    if "sys_sensitive_word" not in existing:
        op.create_table(
            "sys_sensitive_word",
            sa.Column("word", sa.String(length=64), nullable=False, comment="敏感词"),
            sa.Column(
                "category",
                sa.SmallInteger(),
                server_default="9",
                nullable=False,
                comment="分类 1-政治 2-色情低俗 3-违禁品 4-竞品导流 5-诈骗 9-其他",
            ),
            sa.Column(
                "action",
                sa.SmallInteger(),
                server_default="1",
                nullable=False,
                comment="命中处置 1-硬拦截 2-转人工审核",
            ),
            sa.Column(
                "scope",
                sa.String(length=32),
                server_default="all",
                nullable=False,
                comment="适用范围 all-全平台 ecosystem-服务平台",
            ),
            sa.Column(
                "status",
                sa.SmallInteger(),
                server_default="1",
                nullable=False,
                comment="状态 0-停用 1-启用",
            ),
            sa.Column(
                "hit_count",
                sa.BigInteger(),
                server_default="0",
                nullable=False,
                comment="累计命中次数",
            ),
            sa.Column("last_hit_at", sa.DateTime(), nullable=True, comment="最近命中时间"),
            sa.Column("remark", sa.String(length=255), nullable=True, comment="备注"),
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="主键ID"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=False,
                comment="创建时间",
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=False,
                comment="更新时间",
            ),
            sa.Column(
                "is_deleted",
                sa.SmallInteger(),
                server_default="0",
                nullable=False,
                comment="是否删除 0-否 1-是",
            ),
            sa.PrimaryKeyConstraint("id"),
            comment="敏感词库",
        )
        op.create_index(
            "idx_sw_load", "sys_sensitive_word", ["status", "scope", "is_deleted"],
            unique=False,
        )
        op.create_index("idx_sw_word", "sys_sensitive_word", ["word"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    if "sys_sensitive_word" in existing:
        op.drop_index("idx_sw_word", table_name="sys_sensitive_word")
        op.drop_index("idx_sw_load", table_name="sys_sensitive_word")
        op.drop_table("sys_sensitive_word")
