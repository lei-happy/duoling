"""add_sys_design_module

Revision ID: 0bff076118f7
Revises: b7e3c9a15d24
Create Date: 2026-07-27 20:38:20.119647
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0bff076118f7"
down_revision: Union[str, None] = "b7e3c9a15d24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 仅新增设计对接模块表；autogen 检出的其它历史 drift
    # （注释/server_default/索引重命名/无关表）与本次改动无关，已剔除。
    op.create_table(
        "sys_design_module",
        sa.Column("title", sa.String(length=200), nullable=False, comment="模块/页面名称"),
        sa.Column(
            "product_line",
            sa.String(length=32),
            server_default="other",
            nullable=False,
            comment="端：console/client/mobile/lite/other",
        ),
        sa.Column("description", sa.Text(), nullable=True, comment="需求说明"),
        sa.Column(
            "priority",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="优先级 0低/1中/2高/3紧急",
        ),
        sa.Column(
            "status",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
            comment="状态 0待原型/1原型已出/2设计中/3设计完成/4开发中/5已完成/6已搁置",
        ),
        sa.Column(
            "prototype_files",
            sa.JSON(),
            nullable=True,
            comment="原型文件列表 [{url,name,size}]",
        ),
        sa.Column("figma_url", sa.String(length=500), nullable=True, comment="Figma 分享链接"),
        sa.Column("pm_user_id", sa.BigInteger(), nullable=True, comment="产品负责人 sys_user.id"),
        sa.Column("pm_name", sa.String(length=100), nullable=True, comment="产品负责人姓名快照"),
        sa.Column(
            "designer_user_id", sa.BigInteger(), nullable=True, comment="设计师 sys_user.id"
        ),
        sa.Column(
            "designer_name", sa.String(length=100), nullable=True, comment="设计师姓名快照"
        ),
        sa.Column(
            "developer_user_id",
            sa.BigInteger(),
            nullable=True,
            comment="开发负责人 sys_user.id",
        ),
        sa.Column(
            "developer_name",
            sa.String(length=100),
            nullable=True,
            comment="开发负责人姓名快照",
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            server_default="0",
            nullable=False,
            comment="同列内排序（越小越靠前）",
        ),
        sa.Column("created_by", sa.BigInteger(), nullable=True, comment="创建人 sys_user.id"),
        sa.Column("updated_by", sa.BigInteger(), nullable=True, comment="最后更新人 sys_user.id"),
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
        comment="设计对接模块（原型/Figma/优先级/进度）",
    )
    op.create_index(
        "idx_sys_design_module_priority", "sys_design_module", ["priority"], unique=False
    )
    op.create_index(
        "idx_sys_design_module_product_line",
        "sys_design_module",
        ["product_line"],
        unique=False,
    )
    op.create_index(
        "idx_sys_design_module_status", "sys_design_module", ["status"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_sys_design_module_status", table_name="sys_design_module")
    op.drop_index("idx_sys_design_module_product_line", table_name="sys_design_module")
    op.drop_index("idx_sys_design_module_priority", table_name="sys_design_module")
    op.drop_table("sys_design_module")
