"""add sys_regions coordinates and region_sync_job

Revision ID: e3f7a2b91c04
Revises: da8b9ca41ec2
Create Date: 2026-06-02 20:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e3f7a2b91c04"
down_revision: Union[str, None] = "da8b9ca41ec2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sys_regions",
        sa.Column("citycode", sa.String(length=20), nullable=True, comment="高德 citycode"),
    )
    op.add_column(
        "sys_regions",
        sa.Column(
            "longitude",
            sa.Numeric(precision=10, scale=6),
            nullable=True,
            comment="经度（东经为正）",
        ),
    )
    op.add_column(
        "sys_regions",
        sa.Column(
            "latitude",
            sa.Numeric(precision=10, scale=6),
            nullable=True,
            comment="纬度（北纬为正）",
        ),
    )

    op.create_table(
        "region_sync_job",
        sa.Column("job_id", sa.BigInteger(), autoincrement=True, nullable=False, comment="任务ID"),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False, comment="状态"),
        sa.Column("progress_pct", sa.Integer(), server_default="0", nullable=False, comment="进度0-100"),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("log_text", sa.Text(), nullable=True),
        sa.Column("error_message", sa.String(length=2000), nullable=True),
        sa.Column("total_count", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column(
            "last_update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("job_id"),
        comment="行政区域高德同步任务",
    )


def downgrade() -> None:
    op.drop_table("region_sync_job")
    op.drop_column("sys_regions", "latitude")
    op.drop_column("sys_regions", "longitude")
    op.drop_column("sys_regions", "citycode")
