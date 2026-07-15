"""add sys_menu quick_action

Revision ID: 5520bc187666
Revises: a1c2d3e4f5b6
Create Date: 2026-07-15 19:47:51.999691
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5520bc187666'
down_revision: Union[str, None] = 'a1c2d3e4f5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 仅新增 sys_menu.quick_action 列。
    # autogen 另检出大量 alter_column/index diff，均为存量库与 ORM 的注释/默认值/索引名漂移，
    # 与本次改动无关，故手动剔除，避免误改线上表结构。
    op.add_column(
        'sys_menu',
        sa.Column(
            'quick_action', sa.JSON(), nullable=True,
            comment='快捷操作配置(JSON)：null=不支持；含 icon/name/color/link/group/sort/default',
        ),
    )


def downgrade() -> None:
    op.drop_column('sys_menu', 'quick_action')
