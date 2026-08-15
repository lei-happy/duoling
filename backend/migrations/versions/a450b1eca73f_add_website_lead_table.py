"""add website lead table

新增官网留资线索表 open_website_lead。

autogenerate 原始产物包含大量与本次改动无关的历史 drift（open_platform 的
open_capability / open_credential / open_app / open_mcp_config 未在 env.py 注册，
会被误判为「应删除」；另有一批 comment / server_default 的历史差异）。
这些已在 review 时全部剔除，本文件只保留建表。

Revision ID: a450b1eca73f
Revises: c4a8e91f2b07
Create Date: 2026-08-15 18:40:06.079088
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a450b1eca73f'
down_revision: Union[str, None] = 'c4a8e91f2b07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "open_website_lead"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    return sa.inspect(bind).has_table(name)


def upgrade() -> None:
    # 应用启动时会给缺失的 open_* 表兜底建表（app/core/events.py），
    # 所以这里先探测一次，避免在已建表的环境上重复 CREATE 报错。
    if _table_exists(_TABLE):
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("company_name", sa.String(length=128), nullable=False, comment="企业名称"),
        sa.Column("contact_person", sa.String(length=32), nullable=False, comment="联系人称呼"),
        sa.Column("contact_phone", sa.String(length=20), nullable=False, comment="联系手机号"),
        sa.Column(
            "fleet_size",
            sa.String(length=16),
            nullable=True,
            comment="自有板车规模 lt10/10-30/30-100/gt100",
        ),
        sa.Column("pain_point", sa.String(length=255), nullable=True, comment="当前最头疼的一件事"),
        sa.Column("profile_answers", sa.Text(), nullable=True, comment="自测画像题 P1-P3 作答 JSON"),
        sa.Column("stage_band", sa.String(length=8), nullable=True, comment="测评档位 L1-L8"),
        sa.Column("stage_name", sa.String(length=32), nullable=True, comment="档位名称，如 数字化推进期"),
        sa.Column("total_score", sa.SmallInteger(), nullable=True, comment="自测总分 0-80"),
        sa.Column("dim_a", sa.SmallInteger(), nullable=True, comment="业务在线 0-20"),
        sa.Column("dim_b", sa.SmallInteger(), nullable=True, comment="数据贯通 0-20"),
        sa.Column("dim_c", sa.SmallInteger(), nullable=True, comment="智能应用 0-20"),
        sa.Column("dim_d", sa.SmallInteger(), nullable=True, comment="经营闭环 0-20"),
        sa.Column("source_page", sa.String(length=64), nullable=True, comment="提交所在页面路径"),
        sa.Column("referrer", sa.String(length=255), nullable=True, comment="来源页 referrer"),
        sa.Column("client_ip", sa.String(length=64), nullable=True, comment="提交方 IP，用于频控"),
        sa.Column("user_agent", sa.String(length=255), nullable=True, comment="浏览器 UA"),
        sa.Column(
            "status",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
            comment="跟进状态 0-待联系 1-已联系 2-已转化 3-无效",
        ),
        sa.Column("follow_remark", sa.Text(), nullable=True, comment="跟进备注"),
        sa.Column("handler_id", sa.Integer(), nullable=True, comment="跟进人平台用户ID"),
        sa.Column("handler_name", sa.String(length=64), nullable=True, comment="跟进人姓名快照"),
        sa.Column("contacted_at", sa.DateTime(), nullable=True, comment="首次联系时间"),
        sa.Column(
            "converted_tenant_code",
            sa.String(length=32),
            nullable=True,
            comment="转化后的租户编码",
        ),
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
        comment="官网留资线索",
    )
    op.create_index(
        op.f("ix_open_website_lead_client_ip"), _TABLE, ["client_ip"], unique=False
    )
    op.create_index(
        op.f("ix_open_website_lead_contact_phone"), _TABLE, ["contact_phone"], unique=False
    )
    op.create_index(
        op.f("ix_open_website_lead_created_at"), _TABLE, ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_open_website_lead_stage_band"), _TABLE, ["stage_band"], unique=False
    )
    op.create_index(
        op.f("ix_open_website_lead_status"), _TABLE, ["status"], unique=False
    )


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    op.drop_index(op.f("ix_open_website_lead_status"), table_name=_TABLE)
    op.drop_index(op.f("ix_open_website_lead_stage_band"), table_name=_TABLE)
    op.drop_index(op.f("ix_open_website_lead_created_at"), table_name=_TABLE)
    op.drop_index(op.f("ix_open_website_lead_contact_phone"), table_name=_TABLE)
    op.drop_index(op.f("ix_open_website_lead_client_ip"), table_name=_TABLE)
    op.drop_table(_TABLE)
