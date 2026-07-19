"""feedback_handle_fields

Revision ID: 42102ef9acac
Revises: 5520bc187666
Create Date: 2026-07-19 21:51:05.623608
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "42102ef9acac"
down_revision: Union[str, None] = "5520bc187666"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sys_feedback",
        sa.Column("user_name", sa.String(length=64), nullable=True, comment="提交时昵称快照"),
    )
    op.add_column(
        "sys_feedback",
        sa.Column("contact_phone", sa.String(length=20), nullable=True, comment="联系电话"),
    )
    op.add_column(
        "sys_feedback",
        sa.Column("handler_id", sa.BigInteger(), nullable=True, comment="处理人平台用户ID"),
    )
    op.add_column(
        "sys_feedback",
        sa.Column("handler_name", sa.String(length=64), nullable=True, comment="处理人姓名快照"),
    )
    op.add_column(
        "sys_feedback",
        sa.Column("replied_at", sa.DateTime(), nullable=True, comment="最近回复时间"),
    )
    op.alter_column(
        "sys_feedback",
        "feedback_type",
        existing_type=sa.SmallInteger(),
        comment="反馈类型 0-建议 1-缺陷 2-投诉 3-其他",
        existing_comment="反馈类型 0-建议 1-bug 2-投诉 3-其他",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "sys_feedback",
        "feedback_type",
        existing_type=sa.SmallInteger(),
        comment="反馈类型 0-建议 1-bug 2-投诉 3-其他",
        existing_comment="反馈类型 0-建议 1-缺陷 2-投诉 3-其他",
        existing_nullable=False,
    )
    op.drop_column("sys_feedback", "replied_at")
    op.drop_column("sys_feedback", "handler_name")
    op.drop_column("sys_feedback", "handler_id")
    op.drop_column("sys_feedback", "contact_phone")
    op.drop_column("sys_feedback", "user_name")
