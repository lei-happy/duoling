"""审批中心 - 审批引擎

领域无关的状态推进机器：start / agree / reject / withdraw / transfer / add_sign / cc，
节点签署判定（或签/会签/依次会签），条件求值，审批人解析，终态业务回调。

详见《08.审批中心/01.审批引擎核心设计》。
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.approval.instance import (
    ApprovalInstance,
    ApprovalInstanceNode,
)
from app.modules.client.models.approval.task import (
    ApprovalTask,
    ApprovalRecord,
    ApprovalCc,
)
from app.modules.client.services.approval import constants as C
from app.modules.client.services.approval import tree as flow_tree
from app.modules.client.services.approval.condition import eval_condition
from app.modules.client.services.approval.resolver import ApproverResolver
from app.modules.client.services.approval.flow_service import ApprovalFlowService
from app.modules.client.services.approval.callback import get_callback


class ApprovalEngine:
    # =====================================================================
    # 提交
    # =====================================================================
    @staticmethod
    async def start(
        db: AsyncSession,
        *,
        biz_type: str,
        biz_id: int,
        biz_no: Optional[str] = None,
        variables: Optional[dict] = None,
        summary: Optional[dict] = None,
        initiator_id: int,
        initiator_dept_id: Optional[int] = None,
    ) -> ApprovalInstance:
        # 防重复：同一业务单不允许并发审批中实例
        existing = (
            await db.execute(
                select(ApprovalInstance).where(
                    ApprovalInstance.biz_type == biz_type,
                    ApprovalInstance.biz_id == biz_id,
                    ApprovalInstance.status == C.INSTANCE_RUNNING,
                    ApprovalInstance.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise BizException("该单据已有审批中的流程，请勿重复提交")

        flow = await ApprovalFlowService.match_flow(db, biz_type, variables)
        if not flow:
            raise BizException(f"未配置可用的审批流程（场景：{biz_type}）")

        await flow_tree.check_initiator_allowed(
            db, flow.process_config, initiator_id, initiator_dept_id
        )

        initiator_name = await ApprovalEngine._user_name(db, initiator_id)
        instance = ApprovalInstance(
            instance_no=await ApprovalEngine._gen_instance_no(db),
            biz_type=biz_type,
            biz_id=biz_id,
            biz_no=biz_no,
            flow_id=flow.id,
            flow_version=flow.version,
            initiator_id=initiator_id,
            initiator_name=initiator_name,
            initiator_dept_id=initiator_dept_id,
            variables=variables,
            summary=summary,
            process_config=flow.process_config,
            status=C.INSTANCE_RUNNING,
            current_node_order=0,
            submitted_at=datetime.now(),
        )
        db.add(instance)
        await db.flush()

        # 冻结节点快照
        if flow.process_config:
            # 画布流程：按提交变量把条件分支树展开为线性执行路径，再落快照
            path = flow_tree.materialize_path(flow.process_config, variables)
            if not path:
                raise BizException("流程未解析到任何可执行的审批节点")
            for n in path:
                db.add(
                    ApprovalInstanceNode(
                        instance_id=instance.id,
                        node_order=n["node_order"],
                        node_key=n.get("node_key"),
                        node_type=n["node_type"],
                        node_name=n["node_name"],
                        approver_type=n["approver_type"],
                        approver_config=n["approver_config"],
                        sign_type=n["sign_type"],
                        condition=None,  # 分支已在展开时确定，无需运行时再判
                        empty_strategy=n["empty_strategy"],
                        allow_transfer=n["allow_transfer"],
                        allow_addsign=n["allow_addsign"],
                        status=C.NODE_NOT_STARTED,
                    )
                )
        else:
            # 兼容旧线性流程：复制 flow_node 快照
            flow_nodes = await ApprovalFlowService.nodes_of(db, flow.id)
            for n in flow_nodes:
                db.add(
                    ApprovalInstanceNode(
                        instance_id=instance.id,
                        node_order=n.node_order,
                        node_type=n.node_type,
                        node_name=n.node_name,
                        approver_type=n.approver_type,
                        approver_config=n.approver_config,
                        sign_type=n.sign_type,
                        condition=n.condition,
                        empty_strategy=n.empty_strategy,
                        allow_transfer=n.allow_transfer,
                        allow_addsign=n.allow_addsign,
                        status=C.NODE_NOT_STARTED,
                    )
                )
        await db.flush()

        await ApprovalEngine._write_record(
            db, instance, node_order=0, operator_id=initiator_id,
            operator_name=initiator_name, action=C.ACTION_SUBMIT,
        )

        await ApprovalEngine._enter_next_node(db, instance, from_order=0)
        await db.flush()
        return instance

    # =====================================================================
    # 审批动作
    # =====================================================================
    @staticmethod
    async def agree(
        db: AsyncSession, *, task_id: int, operator_id: int,
        comment: Optional[str] = None, attachments=None,
    ) -> ApprovalInstance:
        task, instance, node = await ApprovalEngine._load_task_ctx(db, task_id, operator_id)
        task.status = C.TASK_AGREED
        task.comment = comment
        task.attachments = attachments
        task.acted_at = datetime.now()
        await db.flush()
        await ApprovalEngine._write_record(
            db, instance, node_order=node.node_order, operator_id=operator_id,
            operator_name=task.approver_name, action=C.ACTION_AGREE,
            comment=comment, attachments=attachments,
        )
        await ApprovalEngine._judge_after_action(db, instance, node, agreed_task=task)
        await db.flush()
        return instance

    @staticmethod
    async def reject(
        db: AsyncSession, *, task_id: int, operator_id: int,
        comment: str, attachments=None,
    ) -> ApprovalInstance:
        task, instance, node = await ApprovalEngine._load_task_ctx(db, task_id, operator_id)
        if not comment or not comment.strip():
            raise BizException("驳回必须填写意见")
        task.status = C.TASK_REJECTED
        task.comment = comment
        task.attachments = attachments
        task.acted_at = datetime.now()
        await db.flush()
        await ApprovalEngine._write_record(
            db, instance, node_order=node.node_order, operator_id=operator_id,
            operator_name=task.approver_name, action=C.ACTION_REJECT, comment=comment,
            attachments=attachments,
        )
        # 一票否决：节点拒绝 → 实例拒绝
        await ApprovalEngine._invalidate_pending_tasks(db, node.id, exclude_task_id=task.id)
        node.status = C.NODE_REJECTED
        node.finished_at = datetime.now()
        await ApprovalEngine._finalize(db, instance, C.INSTANCE_REJECTED, result_comment=comment)
        await db.flush()
        return instance

    @staticmethod
    async def withdraw(
        db: AsyncSession, *, instance_id: int, operator_id: int, reason: Optional[str] = None
    ) -> ApprovalInstance:
        instance = await ApprovalEngine._get_instance(db, instance_id)
        if instance.status != C.INSTANCE_RUNNING:
            raise BizException("仅审批中的流程可撤回")
        if instance.initiator_id != operator_id:
            raise BizException("只有发起人可以撤回")
        flow = await ApprovalEngine._get_flow(db, instance.flow_id)
        if flow and not flow.allow_withdraw:
            raise BizException("该流程不允许撤回")
        if flow and flow.withdraw_scope == 0 and instance.current_node_order > 1:
            raise BizException("当前流程仅允许在首节点审批前撤回")
        # 失效所有未处理任务
        await ApprovalEngine._invalidate_all_pending(db, instance_id)
        await ApprovalEngine._write_record(
            db, instance, node_order=instance.current_node_order, operator_id=operator_id,
            operator_name=instance.initiator_name, action=C.ACTION_WITHDRAW, comment=reason,
        )
        await ApprovalEngine._finalize(db, instance, C.INSTANCE_WITHDRAWN, result_comment=reason)
        await db.flush()
        return instance

    @staticmethod
    async def transfer(
        db: AsyncSession, *, task_id: int, operator_id: int, target_user_id: int,
        comment: Optional[str] = None,
    ) -> ApprovalInstance:
        task, instance, node = await ApprovalEngine._load_task_ctx(db, task_id, operator_id)
        if not node.allow_transfer:
            raise BizException("当前节点不允许转审")
        if target_user_id == operator_id:
            raise BizException("不能转审给自己")
        task.status = C.TASK_TRANSFERRED
        task.acted_at = datetime.now()
        await db.flush()
        db.add(
            ApprovalTask(
                instance_id=instance.id,
                instance_node_id=node.id,
                node_order=node.node_order,
                approver_id=target_user_id,
                approver_name=await ApprovalEngine._user_name(db, target_user_id),
                assign_source=C.SOURCE_TRANSFER,
                sign_order=task.sign_order,
                status=C.TASK_PENDING,
            )
        )
        await ApprovalEngine._write_record(
            db, instance, node_order=node.node_order, operator_id=operator_id,
            operator_name=task.approver_name, action=C.ACTION_TRANSFER,
            target_user_id=target_user_id, comment=comment,
        )
        await db.flush()
        return instance

    @staticmethod
    async def add_sign(
        db: AsyncSession, *, task_id: int, operator_id: int, target_user_id: int,
        mode: str = "after", comment: Optional[str] = None,
    ) -> ApprovalInstance:
        task, instance, node = await ApprovalEngine._load_task_ctx(db, task_id, operator_id)
        if not node.allow_addsign:
            raise BizException("当前节点不允许加签")
        is_before = mode == "before"
        new_task = ApprovalTask(
            instance_id=instance.id,
            instance_node_id=node.id,
            node_order=node.node_order,
            approver_id=target_user_id,
            approver_name=await ApprovalEngine._user_name(db, target_user_id),
            assign_source=C.SOURCE_ADDSIGN_BEFORE if is_before else C.SOURCE_ADDSIGN_AFTER,
            sign_order=task.sign_order,
            status=C.TASK_PENDING,
        )
        db.add(new_task)
        # 追加到节点已解析审批人列表
        approvers = list(node.resolved_approver_ids or [])
        if target_user_id not in approvers:
            approvers.append(target_user_id)
            node.resolved_approver_ids = approvers
        await ApprovalEngine._write_record(
            db, instance, node_order=node.node_order, operator_id=operator_id,
            operator_name=task.approver_name,
            action=C.ACTION_ADDSIGN_BEFORE if is_before else C.ACTION_ADDSIGN_AFTER,
            target_user_id=target_user_id, comment=comment,
        )
        await db.flush()
        return instance

    @staticmethod
    async def cc(
        db: AsyncSession, *, instance_id: int, operator_id: int, target_user_ids: List[int]
    ) -> ApprovalInstance:
        instance = await ApprovalEngine._get_instance(db, instance_id)
        for uid in target_user_ids:
            db.add(
                ApprovalCc(
                    instance_id=instance.id,
                    node_order=instance.current_node_order,
                    user_id=uid,
                    user_name=await ApprovalEngine._user_name(db, uid),
                    source=2,
                )
            )
        await ApprovalEngine._write_record(
            db, instance, node_order=instance.current_node_order, operator_id=operator_id,
            operator_name=await ApprovalEngine._user_name(db, operator_id), action=C.ACTION_CC,
        )
        await db.flush()
        return instance

    # =====================================================================
    # 节点推进
    # =====================================================================
    @staticmethod
    async def _enter_next_node(
        db: AsyncSession, instance: ApprovalInstance, from_order: int
    ) -> None:
        nodes = await ApprovalEngine._instance_nodes(db, instance.id)
        nxt = next((n for n in nodes if n.node_order > from_order), None)
        if nxt is None:
            await ApprovalEngine._finalize(db, instance, C.INSTANCE_APPROVED)
            return

        # 节点条件不命中 → 跳过
        if not eval_condition(nxt.condition, instance.variables):
            nxt.status = C.NODE_SKIPPED
            nxt.started_at = datetime.now()
            nxt.finished_at = datetime.now()
            await ApprovalEngine._write_record(
                db, instance, node_order=nxt.node_order,
                operator_id=instance.initiator_id, action=C.ACTION_SKIP,
            )
            await db.flush()
            await ApprovalEngine._enter_next_node(db, instance, nxt.node_order)
            return

        # 解析审批人 / 抄送人
        approver_ids = await ApproverResolver.resolve(
            db,
            approver_type=nxt.approver_type,
            approver_config=nxt.approver_config,
            initiator_id=instance.initiator_id,
            initiator_dept_id=instance.initiator_dept_id,
            variables=instance.variables,
        )
        nxt.resolved_approver_ids = approver_ids
        nxt.started_at = datetime.now()

        # 抄送节点：登记抄送，不阻塞
        if nxt.node_type == C.NODE_TYPE_CC:
            for uid in approver_ids:
                db.add(
                    ApprovalCc(
                        instance_id=instance.id, node_order=nxt.node_order,
                        user_id=uid, user_name=await ApprovalEngine._user_name(db, uid),
                        source=1,
                    )
                )
            nxt.status = C.NODE_PASSED
            nxt.finished_at = datetime.now()
            await db.flush()
            await ApprovalEngine._enter_next_node(db, instance, nxt.node_order)
            return

        # 审批节点：审批人为空 → 空策略
        if not approver_ids:
            if nxt.empty_strategy == C.EMPTY_RAISE:
                raise BizException(f"节点「{nxt.node_name}」未解析到审批人")
            nxt.status = C.NODE_PASSED
            nxt.finished_at = datetime.now()
            await ApprovalEngine._write_record(
                db, instance, node_order=nxt.node_order,
                operator_id=instance.initiator_id, action=C.ACTION_AUTO_PASS,
                comment="未解析到审批人，按策略自动通过",
            )
            await db.flush()
            await ApprovalEngine._enter_next_node(db, instance, nxt.node_order)
            return

        # 正常：进入该节点，生成任务
        nxt.status = C.NODE_RUNNING
        instance.current_node_order = nxt.node_order
        instance.current_node_key = nxt.node_key
        await db.flush()
        await ApprovalEngine._create_tasks_for_node(db, instance, nxt, approver_ids)
        await db.flush()

    @staticmethod
    async def _create_tasks_for_node(
        db: AsyncSession, instance: ApprovalInstance,
        node: ApprovalInstanceNode, approver_ids: List[int],
    ) -> None:
        names = await ApprovalEngine._user_names(db, approver_ids)
        if node.sign_type == C.SIGN_SEQUENTIAL:
            # 仅生成第一个
            first = approver_ids[0]
            db.add(
                ApprovalTask(
                    instance_id=instance.id, instance_node_id=node.id,
                    node_order=node.node_order, approver_id=first,
                    approver_name=names.get(first), assign_source=C.SOURCE_NORMAL,
                    sign_order=0, status=C.TASK_PENDING,
                )
            )
        else:
            for idx, uid in enumerate(approver_ids):
                db.add(
                    ApprovalTask(
                        instance_id=instance.id, instance_node_id=node.id,
                        node_order=node.node_order, approver_id=uid,
                        approver_name=names.get(uid), assign_source=C.SOURCE_NORMAL,
                        sign_order=idx, status=C.TASK_PENDING,
                    )
                )

    @staticmethod
    async def _judge_after_action(
        db: AsyncSession, instance: ApprovalInstance,
        node: ApprovalInstanceNode, agreed_task: ApprovalTask,
    ) -> None:
        tasks = await ApprovalEngine._node_tasks(db, node.id)

        if node.sign_type == C.SIGN_ANY:
            # 任一同意即节点通过
            node.status = C.NODE_PASSED
            node.finished_at = datetime.now()
            await ApprovalEngine._invalidate_pending_tasks(db, node.id, exclude_task_id=agreed_task.id)
            await db.flush()
            await ApprovalEngine._enter_next_node(db, instance, node.node_order)
            return

        if node.sign_type == C.SIGN_ALL:
            pending = [t for t in tasks if t.status == C.TASK_PENDING]
            if not pending:
                node.status = C.NODE_PASSED
                node.finished_at = datetime.now()
                await db.flush()
                await ApprovalEngine._enter_next_node(db, instance, node.node_order)
            return

        if node.sign_type == C.SIGN_SEQUENTIAL:
            approvers = list(node.resolved_approver_ids or [])
            created = len(tasks)
            if created < len(approvers):
                # 生成下一个
                nxt_uid = approvers[created]
                db.add(
                    ApprovalTask(
                        instance_id=instance.id, instance_node_id=node.id,
                        node_order=node.node_order, approver_id=nxt_uid,
                        approver_name=await ApprovalEngine._user_name(db, nxt_uid),
                        assign_source=C.SOURCE_NORMAL, sign_order=created,
                        status=C.TASK_PENDING,
                    )
                )
                await db.flush()
            else:
                node.status = C.NODE_PASSED
                node.finished_at = datetime.now()
                await db.flush()
                await ApprovalEngine._enter_next_node(db, instance, node.node_order)
            return

    # =====================================================================
    # 终态 + 回调
    # =====================================================================
    @staticmethod
    async def _finalize(
        db: AsyncSession, instance: ApprovalInstance, status: int,
        result_comment: Optional[str] = None,
    ) -> None:
        instance.status = status
        instance.finished_at = datetime.now()
        if result_comment:
            instance.result_comment = result_comment
        await db.flush()

        callback = get_callback(instance.biz_type)
        if callback is None:
            logger.warning(
                f"[审批中心] 实例 {instance.id}（biz_type={instance.biz_type}）"
                f"终态={status} 无业务回调注册，跳过回写"
            )
            return
        try:
            if status == C.INSTANCE_APPROVED:
                await callback.on_approved(db, instance)
            elif status == C.INSTANCE_REJECTED:
                await callback.on_rejected(db, instance)
            elif status == C.INSTANCE_WITHDRAWN:
                await callback.on_cancelled(db, instance)
        except BizException:
            raise
        except Exception as e:  # noqa: BLE001
            logger.exception(f"[审批中心] 业务回调失败 instance={instance.id}: {e!r}")
            raise BizException(f"审批结果回写业务失败：{e}")

    # =====================================================================
    # 内部工具
    # =====================================================================
    @staticmethod
    async def _load_task_ctx(db: AsyncSession, task_id: int, operator_id: int):
        task = (
            await db.execute(
                select(ApprovalTask).where(
                    ApprovalTask.id == task_id, ApprovalTask.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not task:
            raise BizException("审批任务不存在")
        if task.approver_id != operator_id:
            raise BizException("您不是该审批任务的处理人")
        if task.status != C.TASK_PENDING:
            raise BizException("该审批任务已处理")
        instance = await ApprovalEngine._get_instance(db, task.instance_id, for_update=True)
        if instance.status != C.INSTANCE_RUNNING:
            raise BizException("该审批流程已结束")
        node = (
            await db.execute(
                select(ApprovalInstanceNode).where(
                    ApprovalInstanceNode.id == task.instance_node_id
                )
            )
        ).scalar_one_or_none()
        if not node:
            raise BizException("审批节点不存在")
        return task, instance, node

    @staticmethod
    async def _get_instance(
        db: AsyncSession, instance_id: int, for_update: bool = False
    ) -> ApprovalInstance:
        stmt = select(ApprovalInstance).where(
            ApprovalInstance.id == instance_id, ApprovalInstance.is_deleted == 0
        )
        if for_update:
            stmt = stmt.with_for_update()
        instance = (await db.execute(stmt)).scalar_one_or_none()
        if not instance:
            raise BizException("审批实例不存在")
        return instance

    @staticmethod
    async def _get_flow(db: AsyncSession, flow_id):
        if not flow_id:
            return None
        from app.modules.client.models.approval.flow import ApprovalFlow

        return (
            await db.execute(select(ApprovalFlow).where(ApprovalFlow.id == flow_id))
        ).scalar_one_or_none()

    @staticmethod
    async def _instance_nodes(db: AsyncSession, instance_id: int) -> List[ApprovalInstanceNode]:
        rows = await db.execute(
            select(ApprovalInstanceNode)
            .where(ApprovalInstanceNode.instance_id == instance_id)
            .order_by(ApprovalInstanceNode.node_order.asc())
        )
        return list(rows.scalars().all())

    @staticmethod
    async def _node_tasks(db: AsyncSession, instance_node_id: int) -> List[ApprovalTask]:
        rows = await db.execute(
            select(ApprovalTask)
            .where(
                ApprovalTask.instance_node_id == instance_node_id,
                ApprovalTask.is_deleted == 0,
            )
            .order_by(ApprovalTask.sign_order.asc(), ApprovalTask.id.asc())
        )
        return list(rows.scalars().all())

    @staticmethod
    async def _invalidate_pending_tasks(
        db: AsyncSession, instance_node_id: int, exclude_task_id: Optional[int] = None
    ) -> None:
        stmt = (
            update(ApprovalTask)
            .where(
                ApprovalTask.instance_node_id == instance_node_id,
                ApprovalTask.status == C.TASK_PENDING,
            )
            .values(status=C.TASK_SKIPPED)
        )
        if exclude_task_id:
            stmt = stmt.where(ApprovalTask.id != exclude_task_id)
        await db.execute(stmt)

    @staticmethod
    async def _invalidate_all_pending(db: AsyncSession, instance_id: int) -> None:
        await db.execute(
            update(ApprovalTask)
            .where(
                ApprovalTask.instance_id == instance_id,
                ApprovalTask.status == C.TASK_PENDING,
            )
            .values(status=C.TASK_SKIPPED)
        )

    @staticmethod
    async def _write_record(
        db: AsyncSession, instance: ApprovalInstance, *, node_order: int,
        operator_id: int, action: int, operator_name: Optional[str] = None,
        target_user_id: Optional[int] = None, comment: Optional[str] = None,
        attachments=None,
    ) -> None:
        db.add(
            ApprovalRecord(
                instance_id=instance.id, node_order=node_order,
                operator_id=operator_id, operator_name=operator_name, action=action,
                target_user_id=target_user_id, comment=comment, attachments=attachments,
            )
        )

    @staticmethod
    async def _gen_instance_no(db: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"SP{today}"
        cnt = (
            await db.execute(
                select(func.count()).select_from(ApprovalInstance.__table__).where(
                    ApprovalInstance.instance_no.like(f"{prefix}%")
                )
            )
        ).scalar() or 0
        return f"{prefix}{cnt + 1:03d}"

    @staticmethod
    async def _user_name(db: AsyncSession, user_id: int) -> Optional[str]:
        if not user_id:
            return None
        user = (
            await db.execute(
                select(BizUser).where(BizUser.id == user_id, BizUser.is_deleted == 0)
            )
        ).scalar_one_or_none()
        if not user:
            return None
        return user.real_name or user.nickname or user.phone

    @staticmethod
    async def _user_names(db: AsyncSession, user_ids: List[int]) -> Dict[int, Optional[str]]:
        if not user_ids:
            return {}
        rows = await db.execute(
            select(BizUser).where(BizUser.id.in_(user_ids), BizUser.is_deleted == 0)
        )
        result: Dict[int, Optional[str]] = {}
        for u in rows.scalars().all():
            result[u.id] = u.real_name or u.nickname or u.phone
        return result
