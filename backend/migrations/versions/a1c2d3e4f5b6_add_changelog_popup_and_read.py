"""add changelog popup flag and read table

Revision ID: a1c2d3e4f5b6
Revises: 912a1d8151db
Create Date: 2026-07-14 12:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1c2d3e4f5b6'
down_revision: Union[str, None] = '912a1d8151db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. sys_changelog 增加"租户端是否强制弹框"字段（带 server_default，兼容存量数据）
    op.add_column(
        'sys_changelog',
        sa.Column(
            'is_popup', sa.SmallInteger(), server_default='0', nullable=False,
            comment='租户端是否弹框强提醒 0-否 1-是',
        ),
    )
    # 2. 新增版本升级说明用户已读记录表
    op.create_table(
        'sys_changelog_read',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('changelog_id', sa.BigInteger(), nullable=False, comment='更新记录ID'),
        sa.Column('tenant_code', sa.String(length=32), nullable=True, comment='租户编码（冗余，便于统计）'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='用户ID'),
        sa.Column('read_at', sa.DateTime(), nullable=False, comment='已读时间'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='版本升级说明用户已读记录表',
    )
    op.create_index('uk_changelog_user', 'sys_changelog_read',
                    ['changelog_id', 'user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('uk_changelog_user', table_name='sys_changelog_read')
    op.drop_table('sys_changelog_read')
    op.drop_column('sys_changelog', 'is_popup')
