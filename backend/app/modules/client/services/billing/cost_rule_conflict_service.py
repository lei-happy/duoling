"""
成本规则冲突检测服务

保存/编辑规则前预校验：同一政策范围下，同 fee_type + 生效期重叠 + 条件树等价
（规范化签名相等）的规则会在匹配时产生同分冲突，这里提前提示。

条件引擎 v2：不再逐列比较线路/车型，而是比较"条件树规范化签名"，
从而覆盖 conditions_json 的 AND/OR 复杂条件；对存量 legacy 规则（无 conditions_json）
其等价 AND 树签名与旧口径（同线路 + 同车型）一致，行为向后兼容。
"""

from __future__ import annotations

import json
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.cost_rule import CostRule


def _date_overlap(
    a_start: Optional[date], a_end: Optional[date],
    b_start: Optional[date], b_end: Optional[date],
) -> bool:
    a_start = a_start or date.min
    a_end = a_end or date.max
    b_start = b_start or date.min
    b_end = b_end or date.max
    return a_start <= b_end and b_start <= a_end


# region_route 的方向（双向）不改变"命中同一线路"的冲突语义，规范化时忽略
_VOLATILE_LEAF_KEYS = {"bidirectional", "is_bidirectional"}


def _canonical(node: Optional[dict]) -> str:
    """把条件树规范化为顺序无关的签名字符串（AND/OR 子节点排序）。"""
    if not node:
        return "∅"
    if "type" in node:
        items = sorted(
            (str(k), str(v)) for k, v in node.items()
            if k not in _VOLATILE_LEAF_KEYS
        )
        return json.dumps({"leaf": items}, ensure_ascii=False, sort_keys=True)
    logic = (node.get("logic") or "and").lower()
    child_sigs = sorted(_canonical(c) for c in (node.get("children") or []))
    return json.dumps({"logic": logic, "children": child_sigs}, ensure_ascii=False)


def condition_signature(tree: Optional[dict]) -> str:
    return _canonical(tree or {})


def _synth_tree(
    origin_region_id: Optional[int],
    destination_region_id: Optional[int],
    brand_id: Optional[int],
    series_id: Optional[int],
) -> dict:
    """由 legacy 入参合成等价 AND 树（与 CostRule.condition_tree 口径一致）。"""
    children: list[dict] = []
    if origin_region_id is not None or destination_region_id is not None:
        children.append({
            "type": "region_route",
            "originRegionId": origin_region_id,
            "destinationRegionId": destination_region_id,
        })
    if series_id is not None:
        children.append({"type": "vehicle_series", "op": "eq", "value": series_id})
    elif brand_id is not None:
        children.append({"type": "vehicle_brand", "op": "eq", "value": brand_id})
    return {"logic": "and", "children": children}


class CostRuleConflictService:

    @staticmethod
    async def check_conflict(
        db: AsyncSession,
        *,
        rule_id: Optional[int],
        policy_id: int,
        fee_type: str,
        origin_region_id: Optional[int] = None,
        destination_region_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        series_id: Optional[int] = None,
        conditions_json: Optional[dict] = None,
        price_type: int = 0,
        effective_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
    ) -> dict:
        # 候选条件树：优先 conditions_json，否则由 legacy 入参合成
        candidate_tree = conditions_json or _synth_tree(
            origin_region_id, destination_region_id, brand_id, series_id,
        )
        candidate_sig = condition_signature(candidate_tree)

        r = await db.execute(
            select(CostRule).where(
                CostRule.policy_id == policy_id,
                CostRule.fee_type == fee_type,
                CostRule.status == 1,
                CostRule.is_deleted == 0,
            )
        )
        conflicts = []
        for other in r.scalars().all():
            if rule_id and other.id == rule_id:
                continue
            if condition_signature(other.condition_tree()) != candidate_sig:
                continue
            if not _date_overlap(
                effective_date, expiry_date,
                other.effective_date, other.expiry_date,
            ):
                continue
            severity = "error" if other.price_type == price_type else "warning"
            conflicts.append({
                "ruleId": other.id,
                "policyId": other.policy_id,
                "feeType": other.fee_type,
                "pricingMethod": other.pricing_method,
                "unitPrice": float(other.unit_price) if other.unit_price is not None else None,
                "priceType": other.price_type,
                "priority": other.priority,
                "ruleVersion": other.rule_version,
                "effectiveDate": other.effective_date.isoformat() if other.effective_date else None,
                "expiryDate": other.expiry_date.isoformat() if other.expiry_date else None,
                "severity": severity,
            })
        return {
            "conflicts": conflicts,
            "hasError": any(c["severity"] == "error" for c in conflicts),
            "count": len(conflicts),
        }
