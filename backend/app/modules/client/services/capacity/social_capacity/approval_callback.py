"""社会运力准入审核 - 审批中心接入回调

场景码：``social_capacity_audit``（仅承接 profile_change 档案准入；status_change 状态变更
仍走旧单级直审，不接入引擎）。

引擎在实例终态时**同事务**回调此处，由社会运力侧推进自身审核状态机并写流水。
所有方法需幂等（以业务单当前状态判重）。

详见《08.审批中心/02.业务接入规范》§6.2。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from loguru import logger
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.approval.task import ApprovalRecord
from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.services.approval import constants as AC
from app.modules.client.services.capacity.social_capacity.social_capacity_audit_service import (
    SocialCapacityAuditService,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_WITHDRAW,
)


BIZ_TYPE_SOCIAL_CAPACITY_AUDIT = "social_capacity_audit"

APPROVAL_DRAFT = 0
APPROVAL_PENDING = 1
APPROVAL_APPROVED = 2
APPROVAL_REJECTED = 3

STATUS_INACTIVE = 0
STATUS_ACTIVE = 1


class SocialCapacityApprovalCallback:
    """社会运力档案准入审核回调。"""

    biz_type = BIZ_TYPE_SOCIAL_CAPACITY_AUDIT

    # ------------------------------------------------------------------
    async def build_summary(self, db: AsyncSession, biz_id: int) -> Dict[str, Any]:
        capacity = await self._load(db, biz_id)
        if not capacity:
            return {}
        return {
            "title": capacity.social_code,
            "运力编号": capacity.social_code,
            "驾驶员": capacity.driver_name,
            "联系电话": capacity.driver_phone,
            "车牌号": capacity.plate_number,
            "车辆类型": capacity.vehicle_type_label,
            "来源": capacity.source,
        }

    # ------------------------------------------------------------------
    async def on_approved(self, db: AsyncSession, instance: Any) -> None:
        capacity = await self._load(db, instance.biz_id)
        if not capacity:
            logger.warning(f"[社会运力审批回调] 运力不存在 biz_id={instance.biz_id}，跳过")
            return
        if capacity.approval_status == APPROVAL_APPROVED:
            return  # 幂等

        operator_id, operator_name, comment = await self._last_action(
            db, instance.id, AC.ACTION_AGREE
        )

        capacity.approval_status = APPROVAL_APPROVED
        capacity.approval_user_id = operator_id
        capacity.approval_time = datetime.now()
        capacity.approval_remark = comment
        if capacity.status == STATUS_INACTIVE:
            capacity.status = STATUS_ACTIVE
        await db.flush()

        # 复用社会运力审核快照（变更对比基线）
        from app.modules.client.services.capacity.social_capacity.social_capacity_service import (
            SocialCapacityService,
        )

        _, vehicle, driver = await SocialCapacityService._load_capacity_entities(
            db, capacity.id
        )
        snapshot = SocialCapacityService._build_audit_snapshot(capacity, vehicle, driver)

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_APPROVE,
            before_status=APPROVAL_PENDING,
            after_status=APPROVAL_APPROVED,
            operator_user_id=operator_id or 0,
            operator_name=operator_name,
            remark=comment,
            attachment={"snapshot": snapshot},
            approval_flow_inst_id=instance.id,
        )

    # ------------------------------------------------------------------
    async def on_rejected(self, db: AsyncSession, instance: Any) -> None:
        capacity = await self._load(db, instance.biz_id)
        if not capacity:
            return
        if capacity.approval_status == APPROVAL_REJECTED:
            return  # 幂等

        operator_id, operator_name, comment = await self._last_action(
            db, instance.id, AC.ACTION_REJECT
        )
        capacity.approval_status = APPROVAL_REJECTED
        capacity.approval_user_id = operator_id
        capacity.approval_time = datetime.now()
        capacity.approval_remark = comment
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_REJECT,
            before_status=APPROVAL_PENDING,
            after_status=APPROVAL_REJECTED,
            operator_user_id=operator_id or 0,
            operator_name=operator_name,
            remark=comment,
            approval_flow_inst_id=instance.id,
        )

    # ------------------------------------------------------------------
    async def on_cancelled(self, db: AsyncSession, instance: Any) -> None:
        capacity = await self._load(db, instance.biz_id)
        if not capacity:
            return
        if capacity.approval_status == APPROVAL_DRAFT:
            return  # 幂等

        operator_id, operator_name, comment = await self._last_action(
            db, instance.id, AC.ACTION_WITHDRAW
        )
        capacity.approval_status = APPROVAL_DRAFT
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_WITHDRAW,
            before_status=APPROVAL_PENDING,
            after_status=APPROVAL_DRAFT,
            operator_user_id=operator_id or instance.initiator_id or 0,
            operator_name=operator_name or instance.initiator_name,
            remark=comment,
            approval_flow_inst_id=instance.id,
        )

    # ------------------------------------------------------------------
    @staticmethod
    async def _load(db: AsyncSession, biz_id: int) -> Optional[SocialCapacity]:
        return (
            await db.execute(
                select(SocialCapacity).where(
                    SocialCapacity.id == biz_id,
                    SocialCapacity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()

    @staticmethod
    async def _last_action(
        db: AsyncSession, instance_id: int, action: int
    ) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """取实例下指定动作的最近一条流水：(operator_id, operator_name, comment)。"""
        rec = (
            await db.execute(
                select(ApprovalRecord)
                .where(
                    ApprovalRecord.instance_id == instance_id,
                    ApprovalRecord.action == action,
                    ApprovalRecord.is_deleted == 0,
                )
                .order_by(desc(ApprovalRecord.id))
                .limit(1)
            )
        ).scalar_one_or_none()
        if not rec:
            return None, None, None
        return rec.operator_id, rec.operator_name, rec.comment


def register() -> None:
    """注册到审批中心回调表（由 lifespan 启动时调用）。"""
    from app.modules.client.services.approval.callback import register_callback

    register_callback(SocialCapacityApprovalCallback())
