"""add promotion banner tables

Revision ID: 912a1d8151db
Revises: e3f7a2b91c04
Create Date: 2026-07-14 10:02:01.626692
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '912a1d8151db'
down_revision: Union[str, None] = 'e3f7a2b91c04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 仅新增推广位 Banner 相关两张平台表；autogen 检出的其它历史 drift
    # （注释/server_default/索引重命名）与本次改动无关，已剔除。
    op.create_table(
        'sys_promotion_banner',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('title', sa.String(length=100), nullable=False, comment='内部标题/运营备注名'),
        sa.Column('image_url', sa.String(length=500), nullable=False, comment='图片地址'),
        sa.Column('link_type', sa.String(length=16), server_default='none', nullable=False,
                  comment='跳转类型 none-只看不跳 external-外链 internal-站内路由'),
        sa.Column('link_url', sa.String(length=500), nullable=True, comment='跳转地址（link_type=none 时为空）'),
        sa.Column('open_in_new_tab', sa.SmallInteger(), server_default='1', nullable=False,
                  comment='外链是否新标签打开 0-否 1-是'),
        sa.Column('target_type', sa.String(length=16), server_default='all', nullable=False,
                  comment='投放定向 all-全部 version-按产品版本 tenant-指定租户'),
        sa.Column('target_values', sa.JSON(), nullable=True, comment='定向白名单：version_code 列表或 tenant_code 列表'),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False, comment='轮播排序，小在前'),
        sa.Column('status', sa.String(length=16), server_default='draft', nullable=False,
                  comment='状态 draft-草稿 published-上线 offline-下线'),
        sa.Column('start_at', sa.DateTime(), nullable=True, comment='生效时间（NULL 不限）'),
        sa.Column('end_at', sa.DateTime(), nullable=True, comment='失效时间（NULL 不限）'),
        sa.Column('remark', sa.String(length=255), nullable=True, comment='备注'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='配置人用户ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='首页推广位 Banner 配置表',
    )
    op.create_table(
        'sys_promotion_banner_event',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('banner_id', sa.BigInteger(), nullable=False, comment='Banner ID'),
        sa.Column('tenant_code', sa.String(length=32), nullable=False, comment='租户编码'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='用户ID'),
        sa.Column('user_phone', sa.String(length=20), nullable=True, comment='用户手机号（冗余，便于展示）'),
        sa.Column('event_type', sa.String(length=16), nullable=False, comment='事件类型 view-曝光 click-点击'),
        sa.Column('occurred_at', sa.DateTime(), nullable=False, comment='发生时间'),
        sa.Column('user_agent', sa.String(length=255), nullable=True, comment='User-Agent（排查用）'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='推广位 Banner 埋点明细表',
    )
    op.create_index('idx_banner_event', 'sys_promotion_banner_event',
                    ['banner_id', 'event_type', 'occurred_at'], unique=False)
    op.create_index('idx_tenant_event', 'sys_promotion_banner_event',
                    ['tenant_code', 'occurred_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_tenant_event', table_name='sys_promotion_banner_event')
    op.drop_index('idx_banner_event', table_name='sys_promotion_banner_event')
    op.drop_table('sys_promotion_banner_event')
    op.drop_table('sys_promotion_banner')
