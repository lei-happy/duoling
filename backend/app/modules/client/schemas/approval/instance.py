"""审批中心 - 实例 / 任务 / 记录 Schema"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 提交（业务侧一般不直接走 HTTP，由 ApprovalEngine.start 内部使用，这里仅作开放接口预留）
# ---------------------------------------------------------------------------
class StartApprovalIn(BaseModel):
    bizType: str
    bizId: int
    bizNo: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# 审批动作
# ---------------------------------------------------------------------------
class ApprovalActionIn(BaseModel):
    comment: Optional[str] = None
    attachments: Optional[Any] = None


class ApprovalRejectIn(BaseModel):
    comment: str
    attachments: Optional[Any] = None


class WithdrawIn(BaseModel):
    reason: Optional[str] = None


class TransferIn(BaseModel):
    targetUserId: int
    comment: Optional[str] = None


class AddSignIn(BaseModel):
    targetUserId: int
    mode: str = "after"  # before | after
    comment: Optional[str] = None


class CcIn(BaseModel):
    targetUserIds: List[int]


# ---------------------------------------------------------------------------
# 列表项 / 详情
# ---------------------------------------------------------------------------
class ApprovalListItem(BaseModel):
    instanceId: int
    taskId: Optional[int] = None  # 待办视角下当前用户的 task
    instanceNo: Optional[str] = None
    bizType: str
    bizId: int
    bizNo: Optional[str] = None
    title: Optional[str] = None
    initiatorId: int
    initiatorName: Optional[str] = None
    status: int
    currentNodeOrder: int
    summary: Optional[Dict[str, Any]] = None
    submittedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None


class ApprovalTaskOut(BaseModel):
    id: int
    nodeOrder: int
    approverId: int
    approverName: Optional[str] = None
    assignSource: int
    signOrder: int
    status: int
    comment: Optional[str] = None
    actedAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "ApprovalTaskOut":
        return cls(
            id=m.id,
            nodeOrder=m.node_order,
            approverId=m.approver_id,
            approverName=m.approver_name,
            assignSource=m.assign_source,
            signOrder=m.sign_order,
            status=m.status,
            comment=m.comment,
            actedAt=m.acted_at,
        )


class ApprovalNodeOut(BaseModel):
    id: int
    nodeOrder: int
    nodeType: int
    nodeName: str
    signType: int
    status: int
    resolvedApproverIds: Optional[List[int]] = None
    tasks: List[ApprovalTaskOut] = []

    @classmethod
    def from_model(cls, m, tasks: Optional[List] = None) -> "ApprovalNodeOut":
        return cls(
            id=m.id,
            nodeOrder=m.node_order,
            nodeType=m.node_type,
            nodeName=m.node_name,
            signType=m.sign_type,
            status=m.status,
            resolvedApproverIds=m.resolved_approver_ids,
            tasks=[ApprovalTaskOut.from_model(t) for t in (tasks or [])],
        )


class ApprovalRecordOut(BaseModel):
    id: int
    nodeOrder: int
    operatorId: int
    operatorName: Optional[str] = None
    action: int
    targetUserId: Optional[int] = None
    comment: Optional[str] = None
    attachments: Optional[Any] = None
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "ApprovalRecordOut":
        return cls(
            id=m.id,
            nodeOrder=m.node_order,
            operatorId=m.operator_id,
            operatorName=m.operator_name,
            action=m.action,
            targetUserId=m.target_user_id,
            comment=m.comment,
            attachments=m.attachments,
            createdAt=m.created_at,
        )


class ApprovalCcOut(BaseModel):
    id: int
    userId: int
    userName: Optional[str] = None
    isRead: int
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "ApprovalCcOut":
        return cls(
            id=m.id,
            userId=m.user_id,
            userName=m.user_name,
            isRead=m.is_read,
            createdAt=m.created_at,
        )


class ApprovalDetailOut(BaseModel):
    instanceId: int
    instanceNo: Optional[str] = None
    bizType: str
    bizId: int
    bizNo: Optional[str] = None
    flowId: Optional[int] = None
    initiatorId: int
    initiatorName: Optional[str] = None
    initiatorDeptId: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    status: int
    currentNodeOrder: int
    resultComment: Optional[str] = None
    submittedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    # 当前登录用户在该实例下可处理的待办（待办视角）
    myPendingTaskId: Optional[int] = None
    canWithdraw: bool = False
    nodes: List[ApprovalNodeOut] = []
    records: List[ApprovalRecordOut] = []
    ccList: List[ApprovalCcOut] = []
