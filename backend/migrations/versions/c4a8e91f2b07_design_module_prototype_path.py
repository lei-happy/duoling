"""design_module_prototype_path

Revision ID: c4a8e91f2b07
Revises: 0bff076118f7
Create Date: 2026-07-27 20:55:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "c4a8e91f2b07"
down_revision: Union[str, None] = "0bff076118f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sys_design_module",
        sa.Column(
            "prototype_path",
            sa.String(length=500),
            nullable=True,
            comment="原型 HTML 相对路径（相对仓库 prototype/ 目录）",
        ),
    )
    op.drop_column("sys_design_module", "prototype_files")


def downgrade() -> None:
    op.add_column(
        "sys_design_module",
        sa.Column(
            "prototype_files",
            mysql.JSON(),
            nullable=True,
            comment="原型文件列表 [{url,name,size}]",
        ),
    )
    op.drop_column("sys_design_module", "prototype_path")
