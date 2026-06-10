"""审批中心 - 流程模板服务

负责模板的增删改查、发布/停用，以及按 biz_type + variables 的流程匹配。
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.approval.flow import ApprovalFlow, ApprovalFlowNode
from app.modules.client.schemas.approval.flow import (
    FlowCreate,
    FlowUpdate,
    FlowOut,
)
from app.modules.client.services.approval import constants as C
from app.modules.client.services.approval.condition import eval_condition

FLOW_DRAFT = 0
FLOW_PUBLISHED = 1
FLOW_DISABLED = 2


class ApprovalFlowService:
    # ---------------- 查询 ----------------
    @staticmethod
    async def page_flows(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        biz_type: Optional[str] = None,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        base = select(ApprovalFlow).where(ApprovalFlow.is_deleted == 0)
        if biz_type:
            base = base.where(ApprovalFlow.biz_type == biz_type)
        if status is not None:
            base = base.where(ApprovalFlow.status == status)
        if keyword:
            like = f"%{keyword.strip()}%"
            base = base.where(ApprovalFlow.flow_name.like(like))

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        rows = await db.execute(
            base.order_by(ApprovalFlow.priority.asc(), ApprovalFlow.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = rows.scalars().all()
        return {
            "list": [FlowOut.from_model(m).model_dump() for m in items],
            "count": total,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_flow(db: AsyncSession, flow_id: int) -> FlowOut:
        flow = await ApprovalFlowService._get_or_404(db, flow_id)
        nodes = await ApprovalFlowService._nodes_of(db, flow_id)
        return FlowOut.from_model(flow, nodes)

    # ---------------- 写 ----------------
    @staticmethod
    async def create_flow(
        db: AsyncSession, data: FlowCreate, operator_id: Optional[int] = None
    ) -> FlowOut:
        flow = ApprovalFlow(
            biz_type=data.bizType,
            flow_name=data.flowName,
            flow_code=data.flowCode,
            condition=data.condition,
            priority=data.priority,
            is_default=data.isDefault,
            allow_withdraw=data.allowWithdraw,
            withdraw_scope=data.withdrawScope,
            status=FLOW_DRAFT,
            version=1,
            remark=data.remark,
            created_user_id=operator_id,
            updated_user_id=operator_id,
        )
        db.add(flow)
        await db.flush()
        await ApprovalFlowService._replace_nodes(db, flow.id, data.nodes)
        await db.flush()
        return await ApprovalFlowService.get_flow(db, flow.id)

    @staticmethod
    async def update_flow(
        db: AsyncSession, flow_id: int, data: FlowUpdate, operator_id: Optional[int] = None
    ) -> FlowOut:
        flow = await ApprovalFlowService._get_or_404(db, flow_id)
        if data.flowName is not None:
            flow.flow_name = data.flowName
        if data.flowCode is not None:
            flow.flow_code = data.flowCode
        if data.condition is not None:
            flow.condition = data.condition
        if data.priority is not None:
            flow.priority = data.priority
        if data.isDefault is not None:
            flow.is_default = data.isDefault
        if data.allowWithdraw is not None:
            flow.allow_withdraw = data.allowWithdraw
        if data.withdrawScope is not None:
            flow.withdraw_scope = data.withdrawScope
        if data.remark is not None:
            flow.remark = data.remark
        flow.updated_user_id = operator_id
        if data.nodes is not None:
            await ApprovalFlowService._replace_nodes(db, flow_id, data.nodes)
        await db.flush()
        return await ApprovalFlowService.get_flow(db, flow_id)

    @staticmethod
    async def publish_flow(db: AsyncSession, flow_id: int) -> FlowOut:
        flow = await ApprovalFlowService._get_or_404(db, flow_id)
        nodes = await ApprovalFlowService._nodes_of(db, flow_id)
        approval_nodes = [n for n in nodes if n.node_type == C.NODE_TYPE_APPROVAL]
        if not approval_nodes:
            raise BizException("流程至少需要一个审批节点才能发布")
        flow.status = FLOW_PUBLISHED
        flow.version = (flow.version or 0) + 1
        await db.flush()
        return await ApprovalFlowService.get_flow(db, flow_id)

    @staticmethod
    async def disable_flow(db: AsyncSession, flow_id: int) -> FlowOut:
        flow = await ApprovalFlowService._get_or_404(db, flow_id)
        flow.status = FLOW_DISABLED
        await db.flush()
        return await ApprovalFlowService.get_flow(db, flow_id)

    @staticmethod
    async def delete_flow(db: AsyncSession, flow_id: int) -> None:
        flow = await ApprovalFlowService._get_or_404(db, flow_id)
        flow.is_deleted = 1
        await db.flush()

    # ---------------- 匹配 ----------------
    @staticmethod
    async def match_flow(
        db: AsyncSession, biz_type: str, variables: Optional[dict]
    ) -> Optional[ApprovalFlow]:
        rows = await db.execute(
            select(ApprovalFlow)
            .where(
                ApprovalFlow.biz_type == biz_type,
                ApprovalFlow.status == FLOW_PUBLISHED,
                ApprovalFlow.is_deleted == 0,
            )
            .order_by(ApprovalFlow.priority.asc(), ApprovalFlow.id.asc())
        )
        flows = rows.scalars().all()
        if not flows:
            return None
        for f in flows:
            if eval_condition(f.condition, variables):
                return f
        # 兜底默认模板
        for f in flows:
            if f.is_default:
                return f
        return None

    @staticmethod
    async def nodes_of(db: AsyncSession, flow_id: int) -> List[ApprovalFlowNode]:
        return await ApprovalFlowService._nodes_of(db, flow_id)

    # ---------------- 内部 ----------------
    @staticmethod
    async def _get_or_404(db: AsyncSession, flow_id: int) -> ApprovalFlow:
        flow = (
            await db.execute(
                select(ApprovalFlow).where(
                    ApprovalFlow.id == flow_id, ApprovalFlow.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not flow:
            raise BizException("审批流程模板不存在")
        return flow

    @staticmethod
    async def _nodes_of(db: AsyncSession, flow_id: int) -> List[ApprovalFlowNode]:
        rows = await db.execute(
            select(ApprovalFlowNode)
            .where(
                ApprovalFlowNode.flow_id == flow_id,
                ApprovalFlowNode.is_deleted == 0,
            )
            .order_by(ApprovalFlowNode.node_order.asc())
        )
        return list(rows.scalars().all())

    @staticmethod
    async def _replace_nodes(db: AsyncSession, flow_id: int, nodes) -> None:
        """全量替换节点：软删旧的，插入新的。"""
        old = await ApprovalFlowService._nodes_of(db, flow_id)
        for n in old:
            n.is_deleted = 1
        for item in nodes or []:
            db.add(
                ApprovalFlowNode(
                    flow_id=flow_id,
                    node_order=item.nodeOrder,
                    node_type=item.nodeType,
                    node_name=item.nodeName,
                    approver_type=item.approverType,
                    approver_config=item.approverConfig,
                    sign_type=item.signType,
                    condition=item.condition,
                    empty_strategy=item.emptyStrategy,
                    allow_transfer=item.allowTransfer,
                    allow_addsign=item.allowAddsign,
                )
            )
