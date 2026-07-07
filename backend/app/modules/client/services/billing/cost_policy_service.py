"""
成本政策服务（租户库）
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.cost_policy import CostPolicy
from app.modules.client.models.billing.cost_rule import CostRule
from app.modules.client.schemas.billing.cost_policy import (
    CostPolicyCreate,
    CostPolicyOut,
    CostPolicyUpdate,
)
from app.modules.client.services.billing.cost_calc_task_service import (
    CostCalcTaskService,
    TASK_POLICY_CHANGED,
)
from app.modules.client.services.billing.task_cost_calc_service import (
    TaskCostCalcService,
)


POLICY_BILLING_FIELDS = {"scope_type", "scope_id", "carrier_type",
                         "effective_date", "expiry_date"}


async def _enqueue_for_policy(
    db: AsyncSession, policy: CostPolicy, *,
    triggered_by_user_id: Optional[int] = None,
) -> int:
    task_ids = await TaskCostCalcService.find_affected_tasks_for_policy(db, policy)
    if not task_ids:
        return 0
    return await CostCalcTaskService.enqueue_many_tasks(
        db, task_ids,
        task_type=TASK_POLICY_CHANGED,
        source_target_type="policy",
        source_target_id=policy.id,
        priority=5,
        triggered_by_user_id=triggered_by_user_id,
    )


class CostPolicyService:

    @staticmethod
    async def page_policies(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        scope_type: Optional[int] = None,
        carrier_type: Optional[int] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(CostPolicy).where(CostPolicy.is_deleted == 0)
        if keyword:
            base = base.where(
                (CostPolicy.policy_no.contains(keyword))
                | (CostPolicy.policy_name.contains(keyword))
            )
        if scope_type is not None:
            base = base.where(CostPolicy.scope_type == scope_type)
        if carrier_type is not None:
            base = base.where(CostPolicy.carrier_type == carrier_type)
        if status is not None:
            base = base.where(CostPolicy.status == status)

        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        r = await db.execute(
            base.order_by(CostPolicy.created_at.desc(), CostPolicy.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = list(r.scalars().all())

        policy_ids = [p.id for p in items]
        total_by_pid: dict[int, int] = {}
        active_by_pid: dict[int, int] = {}
        if policy_ids:
            today = date.today()
            tot_rows = (await db.execute(
                select(CostRule.policy_id, func.count())
                .where(CostRule.policy_id.in_(policy_ids), CostRule.is_deleted == 0)
                .group_by(CostRule.policy_id)
            )).all()
            for pid, cnt in tot_rows:
                total_by_pid[int(pid)] = int(cnt)
            act_rows = (await db.execute(
                select(CostRule.policy_id, func.count())
                .where(
                    CostRule.policy_id.in_(policy_ids),
                    CostRule.is_deleted == 0,
                    CostRule.status == 1,
                    or_(CostRule.effective_date.is_(None),
                        CostRule.effective_date <= today),
                    or_(CostRule.expiry_date.is_(None),
                        CostRule.expiry_date >= today),
                )
                .group_by(CostRule.policy_id)
            )).all()
            for pid, cnt in act_rows:
                active_by_pid[int(pid)] = int(cnt)

        out_list = []
        for item in items:
            pid = int(item.id)
            row = CostPolicyOut.from_model(item).model_copy(update={
                "ruleCount": total_by_pid.get(pid, 0),
                "activeRuleCount": active_by_pid.get(pid, 0),
            })
            out_list.append(row.model_dump())

        return {"list": out_list, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def get_policy(db: AsyncSession, policy_id: int) -> CostPolicy:
        r = await db.execute(
            select(CostPolicy).where(
                CostPolicy.id == policy_id, CostPolicy.is_deleted == 0,
            )
        )
        policy = r.scalar_one_or_none()
        if not policy:
            raise BizException("成本政策不存在")
        return policy

    @staticmethod
    async def create_policy(
        db: AsyncSession, data: CostPolicyCreate,
        *, current_user_id: Optional[int] = None,
    ) -> CostPolicy:
        existing = await db.execute(
            select(CostPolicy).where(
                CostPolicy.policy_no == data.policyNo,
                CostPolicy.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"政策编号 {data.policyNo} 已存在")

        policy = CostPolicy(
            policy_no=data.policyNo,
            policy_name=data.policyName,
            scope_type=data.scopeType,
            scope_id=data.scopeId,
            carrier_type=data.carrierType,
            effective_date=data.effectiveDate,
            expiry_date=data.expiryDate,
            priority=data.priority or 0,
            remark=data.remark,
            status=0,
            created_by=current_user_id,
            updated_by=current_user_id,
        )
        db.add(policy)
        await db.flush()
        await db.refresh(policy)
        return policy

    @staticmethod
    async def update_policy(
        db: AsyncSession, policy_id: int, data: CostPolicyUpdate,
        *, current_user_id: Optional[int] = None,
    ) -> CostPolicy:
        policy = await CostPolicyService.get_policy(db, policy_id)
        field_map = {
            "policyName": "policy_name",
            "scopeType": "scope_type",
            "scopeId": "scope_id",
            "carrierType": "carrier_type",
            "effectiveDate": "effective_date",
            "expiryDate": "expiry_date",
            "status": "status",
            "priority": "priority",
            "remark": "remark",
        }
        billing_changed = False
        for sf, mf in field_map.items():
            val = getattr(data, sf, None)
            if val is not None:
                if mf in POLICY_BILLING_FIELDS and getattr(policy, mf, None) != val:
                    billing_changed = True
                setattr(policy, mf, val)
        policy.updated_by = current_user_id
        if billing_changed:
            policy.version_no = (policy.version_no or 1) + 1
        await db.flush()
        await db.refresh(policy)

        if billing_changed and policy.status == 1:
            try:
                await _enqueue_for_policy(db, policy, triggered_by_user_id=current_user_id)
            except Exception:
                pass
        return policy

    @staticmethod
    async def activate_policy(
        db: AsyncSession, policy_id: int, *, current_user_id: Optional[int] = None,
    ) -> CostPolicy:
        policy = await CostPolicyService.get_policy(db, policy_id)
        if policy.status not in (0, 3):
            raise BizException("仅草稿/已终止状态的政策可以激活")
        policy.status = 1
        policy.version_no = (policy.version_no or 1) + 1
        policy.updated_by = current_user_id
        await db.flush()
        await db.refresh(policy)
        try:
            await _enqueue_for_policy(db, policy, triggered_by_user_id=current_user_id)
        except Exception:
            pass
        return policy

    @staticmethod
    async def terminate_policy(
        db: AsyncSession, policy_id: int, *, current_user_id: Optional[int] = None,
    ) -> CostPolicy:
        policy = await CostPolicyService.get_policy(db, policy_id)
        if policy.status != 1:
            raise BizException("仅生效中的政策可以终止")
        policy.status = 3
        policy.version_no = (policy.version_no or 1) + 1
        policy.updated_by = current_user_id
        await db.flush()
        await db.refresh(policy)
        try:
            await _enqueue_for_policy(db, policy, triggered_by_user_id=current_user_id)
        except Exception:
            pass
        return policy

    @staticmethod
    async def delete_policy(db: AsyncSession, policy_id: int) -> None:
        policy = await CostPolicyService.get_policy(db, policy_id)
        if policy.status == 1:
            raise BizException("生效中的政策不能删除")
        policy.is_deleted = 1
        await db.flush()
