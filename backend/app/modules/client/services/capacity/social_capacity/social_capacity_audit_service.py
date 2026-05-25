"""
社会运力 - 审核与状态流水服务

每次状态变更（提交 / 撤回 / 通过 / 驳回 / 启用 / 停用 / 加入或移出黑名单）
都会写一条流水。该 Service 仅负责"写入"与"按运力 ID 查询历史流水"。
"""

from typing import Optional, Any

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.capacity.social_capacity.social_capacity_audit import (
    SocialCapacityAudit,
)
from app.modules.client.schemas.capacity.social_capacity.social_capacity_audit import (
    SocialCapacityAuditOut,
)


# 操作码常量（与 schema / 文档一致）
ACTION_SUBMIT = 1       # 提交审核
ACTION_APPROVE = 2      # 审核通过
ACTION_REJECT = 3       # 审核驳回
ACTION_ENABLE = 4       # 启用
ACTION_DISABLE = 5      # 停用
ACTION_BLACKLIST = 6    # 加入黑名单
ACTION_UNBLACKLIST = 7  # 移出黑名单
ACTION_WITHDRAW = 8     # 撤回审核


class SocialCapacityAuditService:
    """审核 / 状态流水服务"""

    @staticmethod
    async def write(
        db: AsyncSession,
        social_capacity_id: int,
        action: int,
        before_status: Optional[int],
        after_status: Optional[int],
        operator_user_id: int,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
        attachment: Optional[Any] = None,
        approval_flow_inst_id: Optional[int] = None,
    ) -> SocialCapacityAudit:
        """写一条审核 / 状态流水（未 commit，由调用方统一管理事务）。"""
        audit = SocialCapacityAudit(
            social_capacity_id=social_capacity_id,
            action=action,
            before_status=before_status,
            after_status=after_status,
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
            attachment=attachment,
            approval_flow_inst_id=approval_flow_inst_id,
        )
        db.add(audit)
        await db.flush()
        await db.refresh(audit)
        return audit

    @staticmethod
    async def list_history(
        db: AsyncSession, social_capacity_id: int
    ) -> list[dict]:
        """查询某运力的全量审核 / 状态流水（按时间倒序）。"""
        result = await db.execute(
            select(SocialCapacityAudit)
            .where(
                SocialCapacityAudit.social_capacity_id == social_capacity_id,
                SocialCapacityAudit.is_deleted == 0,
            )
            .order_by(desc(SocialCapacityAudit.created_at), desc(SocialCapacityAudit.id))
        )
        rows = result.scalars().all()
        return [SocialCapacityAuditOut.from_model(r).model_dump() for r in rows]

    @staticmethod
    async def latest(
        db: AsyncSession, social_capacity_id: int
    ) -> Optional[SocialCapacityAudit]:
        """查询某运力最近一条审核 / 状态流水。"""
        result = await db.execute(
            select(SocialCapacityAudit)
            .where(
                SocialCapacityAudit.social_capacity_id == social_capacity_id,
                SocialCapacityAudit.is_deleted == 0,
            )
            .order_by(desc(SocialCapacityAudit.created_at), desc(SocialCapacityAudit.id))
            .limit(1)
        )
        return result.scalar_one_or_none()
