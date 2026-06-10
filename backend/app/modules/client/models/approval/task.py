"""
审批中心 - 任务 / 记录 / 抄送模型

- ApprovalTask    : 节点展开到每个具体审批人的待办项（"我的待办"数据源）
- ApprovalRecord  : 实例内动作流水（进度时间轴数据源，只追加不修改）
- ApprovalCc      : 抄送记录

设计见《08.审批中心/01.审批引擎核心设计》§二 数据模型。
"""

from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import BigInteger, Integer, SmallInteger, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class ApprovalTask(TenantModelBase):
    """审批任务（待办）"""

    __tablename__ = "biz_approval_task"
    __table_args__ = {"comment": "审批任务（待办）表"}
    __table_tier__ = "business"

    instance_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="所属实例ID"
    )
    instance_node_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="所属实例节点ID"
    )
    node_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="节点序号（冗余）"
    )
    approver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="审批人 user_id"
    )
    approver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="审批人姓名（冗余）"
    )
    assign_source: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="来源 1-正常解析 2-转审 3-前加签 4-后加签",
    )
    sign_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="依次会签顺序（或/会签为0）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-待处理 1-已同意 2-已拒绝 3-已转审失效 4-已跳过",
    )
    comment: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="审批意见"
    )
    attachments: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="附件（url 数组）"
    )
    due_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="预留：超时时间（SLA）"
    )
    acted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处理时间"
    )


class ApprovalRecord(TenantModelBase):
    """审批记录（动作流水）"""

    __tablename__ = "biz_approval_record"
    __table_args__ = {"comment": "审批记录（动作流水）表"}
    __table_tier__ = "business"

    instance_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="所属实例ID"
    )
    node_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="发生节点序号（提交=0）"
    )
    operator_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    action: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="动作 1-提交 2-同意 3-拒绝 4-撤回 5-转审 6-前加签 7-后加签 8-抄送 9-自动通过 10-跳过",
    )
    target_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="动作目标（转审给谁/加签给谁）"
    )
    comment: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="意见"
    )
    attachments: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="附件"
    )


class ApprovalCc(TenantModelBase):
    """抄送记录"""

    __tablename__ = "biz_approval_cc"
    __table_args__ = {"comment": "审批抄送表"}
    __table_tier__ = "business"

    instance_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="所属实例ID"
    )
    node_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="触发抄送的节点序号"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="被抄送人 user_id"
    )
    user_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="被抄送人姓名（冗余）"
    )
    source: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="来源 1-节点配置 2-审批人手动抄送",
    )
    is_read: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否已读 0-否 1-是"
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="已读时间"
    )
