"""add_sys_user_workplace_config

Revision ID: da8b9ca41ec2
Revises: 0001_baseline
Create Date: 2026-05-31 14:24:36.002290
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'da8b9ca41ec2'
down_revision: Union[str, None] = '0001_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'sys_user',
        sa.Column(
            'workplace_config',
            sa.JSON(),
            nullable=True,
            comment='工作台个性化配置（JSON格式）',
        ),
    )


def downgrade() -> None:
    op.drop_column('sys_user', 'workplace_config')
