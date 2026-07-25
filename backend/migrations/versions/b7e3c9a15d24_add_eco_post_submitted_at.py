"""add eco audit workflow columns

Revision ID: b7e3c9a15d24
Revises: a1c4e7b2f083
Create Date: 2026-07-25 20:30:00.000000

说明：补齐运营审核链路缺的三列。

1. sys_eco_post.submitted_at（进入审核队列的时间），并把待审队列索引
   从 (audit_status, created_at) 换成 (audit_status, submitted_at)。
2. sys_eco_tenant_credit.whitelist_revoked_at / whitelist_revoke_reason，
   用于落地「移出白名单后需重新累积 30 天无违规才能再次进入」。没有移出时间，
   抽检发现问题移出的租户第二天就会被自动授予流程放回来，处置等于没发生。

为什么不能沿用 created_at：草稿可能躺三天再提交，编辑核心信息触发的完整重审
更是发生在挂牌创建很久之后。用 created_at 排队列，老草稿会插到队首，
而刚回来重审的挂牌看起来已经等了三天——04.运营审核与风控设计.md §2.6 的
「平均审核时长」「2 小时内处理率」「超时未处理数」三个指标全都会算错。

顺带修正 sys_eco_post_audit.action 的列注释（补 15-延长展示）。

本迁移手写而非 autogenerate：本地开发库存在历史 drift（先例见 dab0f20fa617）。
所有语句带存在性守卫，重复执行安全。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b7e3c9a15d24"
down_revision: Union[str, None] = "a1c4e7b2f083"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "sys_eco_post"
_CREDIT = "sys_eco_tenant_credit"
_OLD_INDEX = "idx_eco_post_audit"


def _columns(inspector, table: str = _TABLE) -> set:
    return {c["name"] for c in inspector.get_columns(table)}


def _indexes(inspector, table: str) -> set:
    return {i["name"] for i in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in set(inspector.get_table_names()):
        return

    if "submitted_at" not in _columns(inspector):
        op.add_column(
            _TABLE,
            sa.Column(
                "submitted_at",
                sa.DateTime(),
                nullable=True,
                comment="进入审核队列的时间（审核队列排序与 SLA 计算基准）",
            ),
        )
        # 已有数据回填：待审的用创建时间兜底，好过留空导致队列排序无依据
        op.execute(
            sa.text(
                f"UPDATE {_TABLE} SET submitted_at = created_at "
                "WHERE submitted_at IS NULL AND audit_status <> 0"
            )
        )

    inspector = sa.inspect(bind)
    existing = _indexes(inspector, _TABLE)
    if _OLD_INDEX in existing:
        op.drop_index(_OLD_INDEX, table_name=_TABLE)
    if _OLD_INDEX not in _indexes(sa.inspect(bind), _TABLE):
        op.create_index(
            _OLD_INDEX, _TABLE, ["audit_status", "submitted_at"], unique=False
        )

    inspector = sa.inspect(bind)
    if _CREDIT in set(inspector.get_table_names()):
        credit_columns = _columns(inspector, _CREDIT)
        if "whitelist_revoked_at" not in credit_columns:
            op.add_column(
                _CREDIT,
                sa.Column(
                    "whitelist_revoked_at",
                    sa.DateTime(),
                    nullable=True,
                    comment="最近被移出白名单的时间",
                ),
            )
        if "whitelist_revoke_reason" not in credit_columns:
            op.add_column(
                _CREDIT,
                sa.Column(
                    "whitelist_revoke_reason",
                    sa.String(length=255),
                    nullable=True,
                    comment="最近被移出白名单的原因",
                ),
            )

    if "sys_eco_post_audit" in set(sa.inspect(bind).get_table_names()):
        op.alter_column(
            "sys_eco_post_audit",
            "action",
            existing_type=sa.SmallInteger(),
            existing_nullable=False,
            comment="动作 1-提交 2-通过 3-驳回 4-重新提交 5-主动下架 6-到期下架 "
                    "7-强制下架 8-源单失效下架 9-成交下架 10-重新上架 "
                    "11-免审直通 12-抽检通过 13-抽检不通过 14-编辑 15-延长展示",
        )
        op.alter_column(
            "sys_eco_post_audit",
            "reason_code",
            existing_type=sa.SmallInteger(),
            existing_nullable=True,
            comment="原因编码（驳回/强制下架原因，见 constants.PostRejectReason）",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in set(inspector.get_table_names()):
        return

    if _OLD_INDEX in _indexes(inspector, _TABLE):
        op.drop_index(_OLD_INDEX, table_name=_TABLE)
    op.create_index(_OLD_INDEX, _TABLE, ["audit_status", "created_at"], unique=False)

    if "submitted_at" in _columns(sa.inspect(bind)):
        op.drop_column(_TABLE, "submitted_at")

    inspector = sa.inspect(bind)
    if _CREDIT in set(inspector.get_table_names()):
        credit_columns = _columns(inspector, _CREDIT)
        if "whitelist_revoke_reason" in credit_columns:
            op.drop_column(_CREDIT, "whitelist_revoke_reason")
        if "whitelist_revoked_at" in credit_columns:
            op.drop_column(_CREDIT, "whitelist_revoked_at")
