"""审批中心 - 查询服务

我的待办 / 我的申请 / 审批记录 / 实例详情。
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.approval.instance import (
    ApprovalInstance,
    ApprovalInstanceNode,
)
from app.modules.client.models.approval.task import (
    ApprovalTask,
    ApprovalRecord,
    ApprovalCc,
)
from app.modules.client.schemas.approval.instance import (
    ApprovalListItem,
    ApprovalDetailOut,
    ApprovalNodeOut,
    ApprovalRecordOut,
    ApprovalCcOut,
    ApprovalTaskOut,
)
from app.modules.client.services.approval import constants as C


def _title_of(instance: ApprovalInstance) -> str:
    summary = instance.summary or {}
    # 优先取 summary.title，否则取第一个值
    if isinstance(summary, dict):
        if summary.get("title"):
            return str(summary["title"])
        for v in summary.values():
            if v:
                return str(v)
    return instance.biz_no or instance.instance_no or f"审批单#{instance.id}"


class ApprovalQueryService:
    @staticmethod
    async def list_pending(
        db: AsyncSession, *, user_id: int, page: int = 1, page_size: int = 20,
        biz_type: Optional[str] = None, keyword: Optional[str] = None,
    ) -> dict:
        """我的待办：当前用户有待处理 task 的审批中实例。"""
        base = (
            select(ApprovalTask, ApprovalInstance)
            .join(ApprovalInstance, ApprovalInstance.id == ApprovalTask.instance_id)
            .where(
                ApprovalTask.approver_id == user_id,
                ApprovalTask.status == C.TASK_PENDING,
                ApprovalTask.is_deleted == 0,
                ApprovalInstance.status == C.INSTANCE_RUNNING,
                ApprovalInstance.is_deleted == 0,
            )
        )
        if biz_type:
            base = base.where(ApprovalInstance.biz_type == biz_type)
        if keyword:
            like = f"%{keyword.strip()}%"
            base = base.where(
                or_(
                    ApprovalInstance.instance_no.like(like),
                    ApprovalInstance.biz_no.like(like),
                    ApprovalInstance.initiator_name.like(like),
                )
            )
        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        rows = await db.execute(
            base.order_by(ApprovalTask.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items: List[dict] = []
        for task, inst in rows.all():
            items.append(
                ApprovalListItem(
                    instanceId=inst.id, taskId=task.id, instanceNo=inst.instance_no,
                    bizType=inst.biz_type, bizId=inst.biz_id, bizNo=inst.biz_no,
                    title=_title_of(inst), initiatorId=inst.initiator_id,
                    initiatorName=inst.initiator_name, status=inst.status,
                    currentNodeOrder=inst.current_node_order, summary=inst.summary,
                    submittedAt=inst.submitted_at, finishedAt=inst.finished_at,
                    createdAt=inst.created_at,
                ).model_dump()
            )
        return {"list": items, "count": total, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def list_initiated(
        db: AsyncSession, *, user_id: int, page: int = 1, page_size: int = 20,
        status: Optional[int] = None, biz_type: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        """我的申请：当前用户发起的实例。"""
        base = select(ApprovalInstance).where(
            ApprovalInstance.initiator_id == user_id,
            ApprovalInstance.is_deleted == 0,
        )
        base = ApprovalQueryService._apply_inst_filters(base, status, biz_type, keyword)
        return await ApprovalQueryService._page_instances(db, base, page, page_size)

    @staticmethod
    async def list_history(
        db: AsyncSession, *, page: int = 1, page_size: int = 20,
        status: Optional[int] = None, biz_type: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        """审批记录：全部实例（按权限范围由上层控制，本期返回全部）。"""
        base = select(ApprovalInstance).where(ApprovalInstance.is_deleted == 0)
        base = ApprovalQueryService._apply_inst_filters(base, status, biz_type, keyword)
        return await ApprovalQueryService._page_instances(db, base, page, page_size)

    @staticmethod
    async def pending_count(db: AsyncSession, *, user_id: int) -> int:
        cnt = (
            await db.execute(
                select(func.count())
                .select_from(ApprovalTask)
                .join(ApprovalInstance, ApprovalInstance.id == ApprovalTask.instance_id)
                .where(
                    ApprovalTask.approver_id == user_id,
                    ApprovalTask.status == C.TASK_PENDING,
                    ApprovalTask.is_deleted == 0,
                    ApprovalInstance.status == C.INSTANCE_RUNNING,
                    ApprovalInstance.is_deleted == 0,
                )
            )
        ).scalar() or 0
        return int(cnt)

    @staticmethod
    async def get_detail(
        db: AsyncSession, *, instance_id: int, current_user_id: Optional[int] = None
    ) -> ApprovalDetailOut:
        instance = (
            await db.execute(
                select(ApprovalInstance).where(
                    ApprovalInstance.id == instance_id,
                    ApprovalInstance.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not instance:
            raise BizException("审批实例不存在")

        nodes = (
            await db.execute(
                select(ApprovalInstanceNode)
                .where(ApprovalInstanceNode.instance_id == instance_id)
                .order_by(ApprovalInstanceNode.node_order.asc())
            )
        ).scalars().all()
        tasks = (
            await db.execute(
                select(ApprovalTask)
                .where(
                    ApprovalTask.instance_id == instance_id,
                    ApprovalTask.is_deleted == 0,
                )
                .order_by(ApprovalTask.sign_order.asc(), ApprovalTask.id.asc())
            )
        ).scalars().all()
        records = (
            await db.execute(
                select(ApprovalRecord)
                .where(ApprovalRecord.instance_id == instance_id, ApprovalRecord.is_deleted == 0)
                .order_by(ApprovalRecord.id.asc())
            )
        ).scalars().all()
        ccs = (
            await db.execute(
                select(ApprovalCc)
                .where(ApprovalCc.instance_id == instance_id, ApprovalCc.is_deleted == 0)
                .order_by(ApprovalCc.id.asc())
            )
        ).scalars().all()

        tasks_by_node: dict[int, list] = {}
        for t in tasks:
            tasks_by_node.setdefault(t.instance_node_id, []).append(t)

        node_outs = [
            ApprovalNodeOut.from_model(n, tasks_by_node.get(n.id, [])) for n in nodes
        ]

        my_task_id = None
        if current_user_id:
            for t in tasks:
                if t.approver_id == current_user_id and t.status == C.TASK_PENDING:
                    my_task_id = t.id
                    break

        can_withdraw = bool(
            current_user_id
            and instance.initiator_id == current_user_id
            and instance.status == C.INSTANCE_RUNNING
        )

        return ApprovalDetailOut(
            instanceId=instance.id, instanceNo=instance.instance_no,
            bizType=instance.biz_type, bizId=instance.biz_id, bizNo=instance.biz_no,
            flowId=instance.flow_id, initiatorId=instance.initiator_id,
            initiatorName=instance.initiator_name, initiatorDeptId=instance.initiator_dept_id,
            variables=instance.variables, summary=instance.summary, status=instance.status,
            currentNodeOrder=instance.current_node_order, resultComment=instance.result_comment,
            submittedAt=instance.submitted_at, finishedAt=instance.finished_at,
            myPendingTaskId=my_task_id, canWithdraw=can_withdraw,
            nodes=node_outs,
            records=[ApprovalRecordOut.from_model(r) for r in records],
            ccList=[ApprovalCcOut.from_model(c) for c in ccs],
        )

    # ---------------- 内部 ----------------
    @staticmethod
    def _apply_inst_filters(base, status, biz_type, keyword):
        if status is not None:
            base = base.where(ApprovalInstance.status == status)
        if biz_type:
            base = base.where(ApprovalInstance.biz_type == biz_type)
        if keyword:
            like = f"%{keyword.strip()}%"
            base = base.where(
                or_(
                    ApprovalInstance.instance_no.like(like),
                    ApprovalInstance.biz_no.like(like),
                    ApprovalInstance.initiator_name.like(like),
                )
            )
        return base

    @staticmethod
    async def _page_instances(db: AsyncSession, base, page: int, page_size: int) -> dict:
        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        rows = await db.execute(
            base.order_by(ApprovalInstance.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = []
        for inst in rows.scalars().all():
            items.append(
                ApprovalListItem(
                    instanceId=inst.id, instanceNo=inst.instance_no, bizType=inst.biz_type,
                    bizId=inst.biz_id, bizNo=inst.biz_no, title=_title_of(inst),
                    initiatorId=inst.initiator_id, initiatorName=inst.initiator_name,
                    status=inst.status, currentNodeOrder=inst.current_node_order,
                    summary=inst.summary, submittedAt=inst.submitted_at,
                    finishedAt=inst.finished_at, createdAt=inst.created_at,
                ).model_dump()
            )
        return {"list": items, "count": total, "total": total, "page": page, "page_size": page_size}
