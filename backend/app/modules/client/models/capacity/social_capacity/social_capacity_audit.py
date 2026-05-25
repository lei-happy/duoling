"""
社会运力 - 审核与状态流水表（租户库）

与 biz_social_capacity 1:N 关联，记录提交 / 撤回 / 通过 / 驳回 / 启用 / 停用 /
加入或移出黑名单的全量动作流水，每条流水即操作快照，不可修改。

预留 approval_flow_inst_id 字段对接未来的审批中心多级审批流。
"""

from typing import Optional, Any
from sqlalchemy import String, SmallInteger, BigInteger, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SocialCapacityAudit(TenantModelBase):
    """社会运力审核与状态流水"""

    __tablename__ = "biz_social_capacity_audit"
    __table_args__ = (
        Index("idx_audit_social_capacity", "social_capacity_id"),
        Index("idx_audit_action", "action"),
        {"comment": "社会运力审核与状态流水表"},
    )
    __table_tier__ = "business"

    social_capacity_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_social_capacity.id"
    )
    action: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment=(
            "操作类型 1-提交审核 2-审核通过 3-审核驳回 "
            "4-启用 5-停用 6-加入黑名单 7-移出黑名单 8-撤回审核"
        ),
    )
    before_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="操作前状态（审核类记 approval_status，启停黑记 status）",
    )
    after_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="操作后状态"
    )
    operator_user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="审核意见 / 状态变更原因"
    )
    attachment: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="预留：审核备查附件"
    )
    approval_flow_inst_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="预留：对接审批中心的多级审批实例 ID",
    )
