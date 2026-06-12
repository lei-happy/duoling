"""审批中心 - 流程模板 Schema"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FlowNodeIn(BaseModel):
    nodeOrder: int
    nodeType: int = 1
    nodeName: str
    approverType: int = 1
    approverConfig: Optional[Dict[str, Any]] = None
    signType: int = 1
    condition: Optional[Dict[str, Any]] = None
    emptyStrategy: int = 1
    allowTransfer: int = 1
    allowAddsign: int = 1


class FlowNodeOut(FlowNodeIn):
    id: int

    @classmethod
    def from_model(cls, m) -> "FlowNodeOut":
        return cls(
            id=m.id,
            nodeOrder=m.node_order,
            nodeType=m.node_type,
            nodeName=m.node_name,
            approverType=m.approver_type,
            approverConfig=m.approver_config,
            signType=m.sign_type,
            condition=m.condition,
            emptyStrategy=m.empty_strategy,
            allowTransfer=m.allow_transfer,
            allowAddsign=m.allow_addsign,
        )


class FlowCreate(BaseModel):
    bizType: str
    flowName: str
    flowCode: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    priority: int = 100
    isDefault: int = 0
    allowWithdraw: int = 1
    withdrawScope: int = 1
    remark: Optional[str] = None
    # 旧线性节点（兼容保留，可不传）
    nodes: Optional[List[FlowNodeIn]] = None
    # 可视化画布流程定义（树/条件分支 JSON）
    processConfig: Optional[Dict[str, Any]] = None


class FlowUpdate(BaseModel):
    flowName: Optional[str] = None
    flowCode: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    isDefault: Optional[int] = None
    allowWithdraw: Optional[int] = None
    withdrawScope: Optional[int] = None
    remark: Optional[str] = None
    nodes: Optional[List[FlowNodeIn]] = None
    processConfig: Optional[Dict[str, Any]] = None


class FlowOut(BaseModel):
    id: int
    bizType: str
    flowName: str
    flowCode: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    priority: int
    isDefault: int
    allowWithdraw: int
    withdrawScope: int
    status: int
    version: int
    remark: Optional[str] = None
    processConfig: Optional[Dict[str, Any]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    nodes: List[FlowNodeOut] = []

    @classmethod
    def from_model(cls, m, nodes: Optional[List] = None) -> "FlowOut":
        return cls(
            id=m.id,
            bizType=m.biz_type,
            flowName=m.flow_name,
            flowCode=m.flow_code,
            condition=m.condition,
            priority=m.priority,
            isDefault=m.is_default,
            allowWithdraw=m.allow_withdraw,
            withdrawScope=m.withdraw_scope,
            status=m.status,
            version=m.version,
            remark=m.remark,
            processConfig=getattr(m, "process_config", None),
            createdAt=m.created_at,
            updatedAt=m.updated_at,
            nodes=[FlowNodeOut.from_model(n) for n in (nodes or [])],
        )
