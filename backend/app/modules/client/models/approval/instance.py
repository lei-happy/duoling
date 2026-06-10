"""
审批中心 - 实例运行时模型

- ApprovalInstance      : 一次具体审批运行时，绑定 biz_type + biz_id
- ApprovalInstanceNode  : 实例创建时冻结的节点快照（避免模板事后修改影响在途实例）

设计见《08.审批中心/01.审批引擎核心设计》§二 数据模型。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import BigInteger, Integer, SmallInteger, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class ApprovalInstance(TenantModelBase):
    """审批实例"""

    __tablename__ = "biz_approval_instance"
    __table_args__ = {"comment": "审批实例表"}
    __table_tier__ = "business"

    instance_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="审批单号 SP{yyyyMMdd}{NNN}"
    )
    biz_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="业务场景码"
    )
    biz_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="业务单据主键"
    )
    biz_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="业务单据展示号（冗余）"
    )
    flow_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="命中的模板ID"
    )
    flow_version: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="命中模板的发布版本（冻结）"
    )
    initiator_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="发起人 user_id"
    )
    initiator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发起人姓名（冗余）"
    )
    initiator_dept_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="发起人提交时所属部门（冻结）"
    )
    variables: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="提交时业务变量（条件/解析用）"
    )
    summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="展示摘要快照（差异化渲染用）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-审批中 1-已通过 2-已拒绝 3-已撤回",
    )
    current_node_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="当前推进到的节点序号"
    )
    result_comment: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="终态结论（如拒绝原因摘要）"
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="提交时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="终态时间"
    )


class ApprovalInstanceNode(TenantModelBase):
    """审批实例节点快照"""

    __tablename__ = "biz_approval_instance_node"
    __table_args__ = {"comment": "审批实例节点快照表"}
    __table_tier__ = "business"

    instance_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="所属实例ID"
    )
    node_order: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="节点序号"
    )
    node_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="节点类型 1-审批 2-抄送"
    )
    node_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="节点名称"
    )
    approver_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="审批人类型（冻结）"
    )
    approver_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="审批人配置（冻结）"
    )
    sign_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="签署方式（冻结）"
    )
    condition: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="节点条件（冻结）"
    )
    empty_strategy: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="空审批人策略（冻结）"
    )
    allow_transfer: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否允许转审"
    )
    allow_addsign: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否允许加签"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-未开始 1-进行中 2-已通过 3-已拒绝 4-已跳过",
    )
    resolved_approver_ids: Mapped[Optional[List[int]]] = mapped_column(
        JSON, nullable=True, comment="解析后的审批人 user_id 数组（含加签）"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="结束时间"
    )
