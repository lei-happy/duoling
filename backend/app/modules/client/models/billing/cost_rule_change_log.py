"""
成本费用规则变更快照（保留修改前/修改后字段全量 JSON）
"""

from typing import Optional

from sqlalchemy import (
    BigInteger,
    Index,
    Integer,
    JSON,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CostRuleChangeLog(TenantModelBase):
    """成本规则变更日志（每次 update/disable/enable/delete/create 都写一条）"""

    __tablename__ = "biz_cost_rule_change_log"
    __table_args__ = (
        Index("idx_crcl_rule", "rule_id"),
        Index("idx_crcl_policy", "policy_id"),
        {"comment": "成本规则变更日志表"},
    )
    __table_tier__ = "business"

    rule_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="成本规则ID"
    )
    policy_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="所属政策ID"
    )
    rule_version_before: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="变更前版本号"
    )
    rule_version_after: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="变更后版本号"
    )
    change_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="变更类型 create/update/disable/enable/delete",
    )
    snapshot_before: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="变更前完整字段快照"
    )
    snapshot_after: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="变更后完整字段快照"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人用户ID"
    )
    affected_task_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="本次变更触发重算的任务数量"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
