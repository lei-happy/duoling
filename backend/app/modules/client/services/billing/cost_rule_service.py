"""
成本费用规则服务（租户库）
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.cost_policy import CostPolicy
from app.modules.client.models.billing.cost_rule import CostRule
from app.modules.client.models.billing.cost_rule_change_log import CostRuleChangeLog
from app.modules.client.schemas.billing.cost_rule import (
    CostRuleCreate,
    CostRuleOut,
    CostRuleUpdate,
)
from app.modules.client.services.billing.cost_calc_task_service import (
    CostCalcTaskService,
    TASK_RULE_CHANGED,
)
from app.modules.client.services.billing.cost_constants import fee_type_name
from app.modules.client.services.billing.task_cost_calc_service import (
    TaskCostCalcService,
)


_SNAPSHOT_FIELDS = [
    "policy_id", "fee_type", "fee_name", "direction", "pricing_method",
    "qty_dimension", "multiply_by_qty", "unit_price", "distance_km",
    "min_amount", "max_amount", "round_mode", "tiers_json", "percent_base",
    "rate_percent", "payee_type", "origin_region_id", "destination_region_id",
    "is_bidirectional", "brand_id", "series_id", "price_type", "priority",
    "status", "rule_version",
]


def _snapshot(rule: CostRule) -> dict:
    out = {}
    for f in _SNAPSHOT_FIELDS:
        v = getattr(rule, f, None)
        out[f] = str(v) if v is not None and not isinstance(v, (int, str)) else v
    return out


async def _enqueue_for_rule(
    db: AsyncSession, rule: CostRule, *,
    triggered_by_user_id: Optional[int] = None,
) -> int:
    task_ids = await TaskCostCalcService.find_affected_tasks_for_rule(db, rule)
    if not task_ids:
        return 0
    return await CostCalcTaskService.enqueue_many_tasks(
        db, task_ids,
        task_type=TASK_RULE_CHANGED,
        source_target_type="rule",
        source_target_id=rule.id,
        priority=5,
        triggered_by_user_id=triggered_by_user_id,
    )


class CostRuleService:

    @staticmethod
    async def list_by_policy(db: AsyncSession, policy_id: int) -> list[dict]:
        r = await db.execute(
            select(CostRule).where(
                CostRule.policy_id == policy_id,
                CostRule.is_deleted == 0,
            ).order_by(CostRule.fee_type, CostRule.id)
        )
        return [CostRuleOut.from_model(m).model_dump() for m in r.scalars().all()]

    @staticmethod
    async def list_rules_cross_policy(
        db: AsyncSession,
        *,
        fee_type: Optional[str] = None,
        scope_type: Optional[int] = None,
        carrier_type: Optional[int] = None,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> list[dict]:
        """费用中心：跨政策罗列全部规则，附带所属政策信息。

        联表 biz_cost_rule × biz_cost_policy，支持按费用类型/范围类型/承运类型/
        关键字（政策名/编号/线路/费用名）筛选。仅用于浏览维护，不触发计算。
        """
        stmt = (
            select(CostRule, CostPolicy)
            .join(CostPolicy, CostRule.policy_id == CostPolicy.id)
            .where(CostRule.is_deleted == 0, CostPolicy.is_deleted == 0)
        )
        if fee_type:
            stmt = stmt.where(CostRule.fee_type == fee_type)
        if scope_type is not None:
            stmt = stmt.where(CostPolicy.scope_type == scope_type)
        if carrier_type is not None:
            stmt = stmt.where(CostPolicy.carrier_type == carrier_type)
        if status is not None:
            stmt = stmt.where(CostRule.status == status)
        if keyword:
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(
                CostPolicy.policy_name.ilike(like),
                CostPolicy.policy_no.ilike(like),
                CostRule.fee_name.ilike(like),
                CostRule.origin.ilike(like),
                CostRule.destination.ilike(like),
            ))
        stmt = stmt.order_by(
            CostRule.fee_type,
            CostPolicy.priority.desc(),
            CostRule.priority.desc(),
            CostRule.id.desc(),
        )
        rows = (await db.execute(stmt)).all()
        out: list[dict] = []
        for rule, policy in rows:
            item = CostRuleOut.from_model(rule).model_dump()
            item["policyName"] = policy.policy_name
            item["policyNo"] = policy.policy_no
            item["policyScopeType"] = policy.scope_type
            item["policyScopeId"] = policy.scope_id
            item["policyCarrierType"] = policy.carrier_type
            item["policyStatus"] = policy.status
            item["policyEffectiveDate"] = (
                policy.effective_date.isoformat() if policy.effective_date else None
            )
            item["policyExpiryDate"] = (
                policy.expiry_date.isoformat() if policy.expiry_date else None
            )
            out.append(item)
        return out

    @staticmethod
    async def get_rule(db: AsyncSession, rule_id: int) -> CostRule:
        r = await db.execute(
            select(CostRule).where(
                CostRule.id == rule_id, CostRule.is_deleted == 0,
            )
        )
        rule = r.scalar_one_or_none()
        if not rule:
            raise BizException("成本规则不存在")
        return rule

    @staticmethod
    async def create_rule(
        db: AsyncSession, policy_id: int, data: CostRuleCreate,
        *, current_user_id: Optional[int] = None,
    ) -> CostRule:
        rule = CostRule(
            policy_id=policy_id,
            fee_type=data.feeType,
            fee_name=data.feeName or fee_type_name(data.feeType),
            direction=data.direction,
            pricing_method=data.pricingMethod,
            qty_dimension=data.qtyDimension,
            multiply_by_qty=data.multiplyByQty,
            unit_price=data.unitPrice,
            distance_km=data.distanceKm,
            min_amount=data.minAmount,
            max_amount=data.maxAmount,
            round_mode=data.roundMode,
            tiers_json=data.tiersJson,
            percent_base=data.percentBase,
            rate_percent=data.ratePercent,
            payee_type=data.payeeType,
            origin_region_id=data.originRegionId,
            origin_code=data.originCode,
            origin=data.origin,
            destination_region_id=data.destinationRegionId,
            destination_code=data.destinationCode,
            destination=data.destination,
            is_bidirectional=data.isBidirectional,
            brand_id=data.brandId,
            series_id=data.seriesId,
            price_type=data.priceType,
            priority=data.priority,
            effective_date=data.effectiveDate,
            expiry_date=data.expiryDate,
            remark=data.remark,
            status=1,
            rule_version=1,
            created_by=current_user_id,
            updated_by=current_user_id,
        )
        db.add(rule)
        await db.flush()
        await db.refresh(rule)

        db.add(CostRuleChangeLog(
            rule_id=rule.id, policy_id=rule.policy_id,
            rule_version_before=None, rule_version_after=rule.rule_version,
            change_type="create", snapshot_before=None,
            snapshot_after=_snapshot(rule), operator_id=current_user_id,
        ))
        await db.flush()
        return rule

    @staticmethod
    async def update_rule(
        db: AsyncSession, rule_id: int, data: CostRuleUpdate,
        *, current_user_id: Optional[int] = None,
    ) -> CostRule:
        rule = await CostRuleService.get_rule(db, rule_id)
        before = _snapshot(rule)
        version_before = rule.rule_version

        field_map = {
            "feeType": "fee_type", "feeName": "fee_name", "direction": "direction",
            "pricingMethod": "pricing_method", "qtyDimension": "qty_dimension",
            "multiplyByQty": "multiply_by_qty", "unitPrice": "unit_price",
            "distanceKm": "distance_km", "minAmount": "min_amount",
            "maxAmount": "max_amount", "roundMode": "round_mode",
            "tiersJson": "tiers_json", "percentBase": "percent_base",
            "ratePercent": "rate_percent", "payeeType": "payee_type",
            "originRegionId": "origin_region_id", "originCode": "origin_code",
            "origin": "origin", "destinationRegionId": "destination_region_id",
            "destinationCode": "destination_code", "destination": "destination",
            "isBidirectional": "is_bidirectional", "brandId": "brand_id",
            "seriesId": "series_id", "priceType": "price_type",
            "priority": "priority", "effectiveDate": "effective_date",
            "expiryDate": "expiry_date", "status": "status", "remark": "remark",
        }
        for sf, mf in field_map.items():
            val = getattr(data, sf, None)
            if val is not None:
                setattr(rule, mf, val)
        rule.rule_version = (rule.rule_version or 1) + 1
        rule.updated_by = current_user_id
        await db.flush()
        await db.refresh(rule)

        db.add(CostRuleChangeLog(
            rule_id=rule.id, policy_id=rule.policy_id,
            rule_version_before=version_before, rule_version_after=rule.rule_version,
            change_type="update", snapshot_before=before,
            snapshot_after=_snapshot(rule), operator_id=current_user_id,
        ))
        await db.flush()

        try:
            await _enqueue_for_rule(db, rule, triggered_by_user_id=current_user_id)
        except Exception:
            pass
        return rule

    @staticmethod
    async def delete_rule(
        db: AsyncSession, rule_id: int, *, current_user_id: Optional[int] = None,
    ) -> None:
        rule = await CostRuleService.get_rule(db, rule_id)
        before = _snapshot(rule)
        rule.is_deleted = 1
        rule.rule_version = (rule.rule_version or 1) + 1
        await db.flush()
        db.add(CostRuleChangeLog(
            rule_id=rule.id, policy_id=rule.policy_id,
            rule_version_before=before.get("rule_version"),
            rule_version_after=rule.rule_version,
            change_type="delete", snapshot_before=before,
            snapshot_after=None, operator_id=current_user_id,
        ))
        await db.flush()
        try:
            await _enqueue_for_rule(db, rule, triggered_by_user_id=current_user_id)
        except Exception:
            pass

    @staticmethod
    async def recalculate_affected(
        db: AsyncSession, rule_id: int, *, current_user_id: Optional[int] = None,
    ) -> dict:
        rule = await CostRuleService.get_rule(db, rule_id)
        task_ids = await TaskCostCalcService.find_affected_tasks_for_rule(db, rule)
        enqueued = await CostCalcTaskService.enqueue_many_tasks(
            db, task_ids,
            task_type=TASK_RULE_CHANGED,
            source_target_type="rule",
            source_target_id=rule.id,
            priority=8,
            triggered_by_user_id=current_user_id,
        )
        return {"affectedTaskCount": len(task_ids), "enqueuedTaskCount": enqueued}
