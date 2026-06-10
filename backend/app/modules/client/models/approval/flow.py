"""
审批中心 - 流程模板模型

- ApprovalFlow      : 某业务场景（biz_type）下的一套可复用审批模板
- ApprovalFlowNode  : 模板中的线性节点（审批节点 / 抄送节点）

设计见《08.审批中心/01.审批引擎核心设计》§二 数据模型。
"""

from typing import Any, Dict, Optional, List

from sqlalchemy import BigInteger, Integer, SmallInteger, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class ApprovalFlow(TenantModelBase):
    """审批流程模板"""

    __tablename__ = "biz_approval_flow"
    __table_args__ = {"comment": "审批流程模板表"}
    __table_tier__ = "business"

    biz_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="业务场景码，如 social_capacity_audit"
    )
    flow_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="模板名称"
    )
    flow_code: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="模板编码（租户内唯一）"
    )
    condition: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="流程级生效条件（JSON DSL），空=默认"
    )
    priority: Mapped[int] = mapped_column(
        Integer, default=100, server_default="100",
        comment="同 biz_type 下匹配优先级（数值小优先）",
    )
    is_default: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否兜底默认模板 0-否 1-是"
    )
    allow_withdraw: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否允许发起人撤回 0-否 1-是"
    )
    withdraw_scope: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="撤回范围 0-仅首节点未审批前 1-审批中任意时刻",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 1-已发布 2-已停用",
    )
    version: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", comment="发布版本号"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
    created_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
    updated_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="更新人"
    )


class ApprovalFlowNode(TenantModelBase):
    """审批流程节点（线性链）"""

    __tablename__ = "biz_approval_flow_node"
    __table_args__ = {"comment": "审批流程节点表"}
    __table_tier__ = "business"

    flow_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="所属模板ID"
    )
    node_order: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="节点序号（从1递增）"
    )
    node_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="节点类型 1-审批节点 2-抄送节点",
    )
    node_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="节点名称"
    )
    approver_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="审批人类型 1-指定成员 2-指定角色 3-指定部门 4-部门负责人 5-逐级上级 6-发起人自选 7-发起人本人",
    )
    approver_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="审批人配置（user_ids/role_ids/dept_ids/level 等）"
    )
    sign_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="签署方式 1-或签ANY 2-会签ALL 3-依次会签SEQUENTIAL",
    )
    condition: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="节点级条件（命中才执行），空=总是执行"
    )
    empty_strategy: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="审批人为空策略 1-自动通过 2-转交管理员 3-报错阻断",
    )
    allow_transfer: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否允许转审 0-否 1-是"
    )
    allow_addsign: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否允许加签 0-否 1-是"
    )
