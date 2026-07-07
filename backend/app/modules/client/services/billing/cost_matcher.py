"""
成本匹配引擎（支出成本引擎 - 纯算法层）

设计要点（与收入侧 FreightMatcher 对称）：
  - 纯算法：所有数据加载由编排层（TaskCostCalcService）完成，本类只接受
    标准化后的输入，不直接访问 DB。
  - 逐费用类型：对每个 fee_type 独立跑一次综合评分匹配并各自计算金额。
  - 综合评分复用收入侧：线路分 / 车型分 / 方向分 / 价格类型分 + 版本 + 人工优先级，
    仅把最外层"客户分"替换为"承运范围 scope 分"。
  - 多车型：限车型规则按车系/品牌分组分别匹配并累加；未限车型按总台数一次算清。
  - match_trace：完整记录命中维度 / 评分明细 / 候选，便于审计与回放。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from typing import Optional

from app.modules.client.models.billing.cost_policy import CostPolicy
from app.modules.client.models.billing.cost_rule import CostRule
from app.modules.client.services.billing.cost_constants import (
    COST_ENGINE_VERSION,
    ERR_DISTANCE_NOT_FOUND,
    ERR_INVALID_QTY,
    ERR_RULE_CONFLICT,
    ERR_RULE_NOT_FOUND,
    KM_METHODS,
    PM_FIXED,
    PM_PER_KM,
    PM_PER_TON_KM,
    PM_PER_TRIP,
    PM_PER_VEHICLE,
    PM_PERCENTAGE,
    PM_TIERED,
    QTY_METHODS,
    SCOPE_SCORE,
    fee_type_is_required,
    fee_type_name,
)
from app.modules.client.services.billing.freight_matcher import (
    DIR_SCORE,
    LINE_SCORE,
    MODEL_SCORE,
    PRICE_TYPE_SCORE,
    VERSION_BONUS_PER,
    FreightMatcher,
)
from app.modules.client.services.billing.standardize_service import (
    REGION_LEVEL_LABEL,
    RegionResolution,
    VehicleResolution,
)


# ---- 数据结构 ----


@dataclass
class VehicleGroup:
    """任务下按车型聚合的一组商品车"""

    vehicle: VehicleResolution
    quantity: int


@dataclass
class TaskCostContext:
    """任务级别的成本匹配上下文"""

    carrier_type: Optional[int]
    transport_date: date
    origin: RegionResolution
    destination: RegionResolution
    total_quantity: int
    vehicle_groups: list[VehicleGroup]
    distance_km: Optional[Decimal] = None          # 线路标准里程
    distance_source: Optional[str] = None          # biz_route / task
    ton: Optional[Decimal] = None                  # 吨位（per_ton_km）
    freight_income: Optional[Decimal] = None       # 收入侧运费合计（percentage 基数）
    payee_id: Optional[int] = None
    payee_name: Optional[str] = None


@dataclass
class FeeItemResult:
    """单个费用项的匹配 + 计算结果"""

    fee_type: str
    fee_name: Optional[str] = None
    direction: int = 1
    payee_type: Optional[int] = None
    pricing_method: Optional[str] = None
    unit_price: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    distance_km: Optional[Decimal] = None
    amount: Decimal = Decimal("0")

    matched_policy_id: Optional[int] = None
    matched_rule_id: Optional[int] = None
    matched_rule_version: Optional[int] = None
    match_score: Optional[int] = None
    match_trace: dict = field(default_factory=dict)

    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def calc_status(self) -> str:
        return "exception" if self.error_type else "success"


@dataclass
class _Candidate:
    rule: CostRule
    policy: CostPolicy
    scope_matched: str
    direction: str
    origin_match_level: str
    destination_match_level: str
    origin_match_region_id: int
    destination_match_region_id: int
    model_match_type: str
    score: int
    score_breakdown: dict


_SCOPE_LABEL = {0: "global", 1: "carrier", 2: "driver", 3: "capacity"}


class CostMatcher:

    # ---------- 金额计算 ----------

    @staticmethod
    def _round(amount: Decimal, round_mode: int) -> Decimal:
        if round_mode == 1:
            return amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        if round_mode == 2:
            return amount.quantize(Decimal("1"), rounding=ROUND_CEILING)
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _resolve_km(rule: CostRule, ctx: TaskCostContext) -> Optional[Decimal]:
        if rule.distance_km is not None:
            return rule.distance_km
        return ctx.distance_km

    @staticmethod
    def _tiered_amount(tiers: Optional[list], qty: Decimal) -> Decimal:
        """阶梯累进：tiers=[{"upTo":100,"unitPrice":5},{"upTo":null,"unitPrice":4}]"""
        if not tiers:
            return Decimal("0")
        remaining = qty
        prev_cap = Decimal("0")
        total = Decimal("0")
        for seg in tiers:
            up_to = seg.get("upTo")
            unit = Decimal(str(seg.get("unitPrice") or 0))
            if up_to is None:
                seg_qty = remaining
            else:
                cap = Decimal(str(up_to))
                seg_qty = min(remaining, cap - prev_cap)
                prev_cap = cap
            if seg_qty <= 0:
                continue
            total += unit * seg_qty
            remaining -= seg_qty
            if remaining <= 0:
                break
        return total

    @staticmethod
    def _calc_amount(
        rule: CostRule, ctx: TaskCostContext, qty: Decimal,
    ) -> tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal], Optional[str]]:
        """返回 (amount, used_quantity, used_km, error_type)"""
        method = rule.pricing_method
        unit = rule.unit_price or Decimal("0")
        used_km: Optional[Decimal] = None

        if method == PM_PER_VEHICLE:
            total = unit * qty
            used_qty = qty
        elif method == PM_PER_KM:
            km = CostMatcher._resolve_km(rule, ctx)
            if km is None:
                return None, None, None, ERR_DISTANCE_NOT_FOUND
            used_km = km
            mult = qty if rule.multiply_by_qty == 1 else Decimal("1")
            total = unit * km * mult
            used_qty = mult
        elif method == PM_PER_TRIP:
            total = unit
            used_qty = Decimal("1")
        elif method == PM_FIXED:
            total = unit
            used_qty = Decimal("1")
        elif method == PM_PER_TON_KM:
            km = CostMatcher._resolve_km(rule, ctx)
            if km is None:
                return None, None, None, ERR_DISTANCE_NOT_FOUND
            used_km = km
            ton = ctx.ton or Decimal("0")
            total = unit * ton * km
            used_qty = ton
        elif method == PM_PERCENTAGE:
            base = ctx.freight_income or Decimal("0")
            rate = rule.rate_percent or Decimal("0")
            total = base * rate / Decimal("100")
            used_qty = base
        elif method == PM_TIERED:
            total = CostMatcher._tiered_amount(rule.tiers_json, qty)
            used_qty = qty
        else:
            total = unit * qty
            used_qty = qty

        # 保底 / 封顶
        if rule.min_amount is not None and total < rule.min_amount:
            total = rule.min_amount
        if rule.max_amount is not None and total > rule.max_amount:
            total = rule.max_amount
        # 取整
        total = CostMatcher._round(total, rule.round_mode or 0)
        return total, used_qty, used_km, None

    # ---------- 候选构造与评分 ----------

    @staticmethod
    def _build_candidates_for_rule(
        rule: CostRule,
        policy: CostPolicy,
        ctx: TaskCostContext,
        vehicle: VehicleResolution,
        region_level_cache: dict[int, str],
    ) -> list[_Candidate]:
        out: list[_Candidate] = []

        # 车型维度
        model_type = FreightMatcher._model_match_type(rule, vehicle)
        if model_type is None:
            return out

        scope_s = SCOPE_SCORE.get(policy.scope_type, 0)
        scope_label = _SCOPE_LABEL.get(policy.scope_type, "global")

        # 线路维度：规则未限线路 → 通用命中
        if rule.origin_region_id is None and rule.destination_region_id is None:
            model_s = MODEL_SCORE.get(model_type, 0)
            price_type_s = PRICE_TYPE_SCORE.get(rule.price_type, 0)
            version_s = (rule.rule_version or 1) * VERSION_BONUS_PER
            total = (
                scope_s + 5_000 + model_s + price_type_s + version_s
                + (policy.priority or 0) + (rule.priority or 0)
            )
            out.append(_Candidate(
                rule=rule, policy=policy, scope_matched=scope_label,
                direction="general",
                origin_match_level="any", destination_match_level="any",
                origin_match_region_id=0, destination_match_region_id=0,
                model_match_type=model_type, score=total,
                score_breakdown={
                    "scope": scope_s, "scope_label": scope_label,
                    "line": 5_000, "line_pair": "any",
                    "model": model_s, "model_layer": model_type,
                    "price_type": price_type_s, "version": version_s,
                    "policy_priority": (policy.priority or 0),
                    "rule_priority": (rule.priority or 0),
                },
            ))
            return out

        # 限线路：按区域链路展开评分
        origin_chain = [(n.region_id, n.level_label) for n in ctx.origin.chain]
        dest_chain = [(n.region_id, n.level_label) for n in ctx.destination.chain]
        for oid, ol in origin_chain:
            for did, dl in dest_chain:
                direction = FreightMatcher._direction_for(rule, oid, did)
                if direction is None:
                    continue
                rule_o_level, rule_d_level = FreightMatcher._resolve_rule_levels(
                    rule, region_level_cache
                )
                line_s = LINE_SCORE.get((rule_o_level, rule_d_level), 5_000)
                model_s = MODEL_SCORE.get(model_type, 0)
                dir_s = DIR_SCORE.get(direction, 0)
                price_type_s = PRICE_TYPE_SCORE.get(rule.price_type, 0)
                version_s = (rule.rule_version or 1) * VERSION_BONUS_PER
                total = (
                    scope_s + line_s + model_s + dir_s + price_type_s + version_s
                    + (policy.priority or 0) + (rule.priority or 0)
                )
                out.append(_Candidate(
                    rule=rule, policy=policy, scope_matched=scope_label,
                    direction=direction,
                    origin_match_level=ol, destination_match_level=dl,
                    origin_match_region_id=oid, destination_match_region_id=did,
                    model_match_type=model_type, score=total,
                    score_breakdown={
                        "scope": scope_s, "scope_label": scope_label,
                        "line": line_s, "line_pair": f"{rule_o_level}->{rule_d_level}",
                        "model": model_s, "model_layer": model_type,
                        "direction": dir_s, "direction_label": direction,
                        "price_type": price_type_s, "version": version_s,
                        "policy_priority": (policy.priority or 0),
                        "rule_priority": (rule.priority or 0),
                    },
                ))
        return out

    @staticmethod
    def _select_best(
        candidates: list[CostRule],
        policy_map: dict[int, CostPolicy],
        ctx: TaskCostContext,
        vehicle: VehicleResolution,
        region_level_cache: dict[int, str],
    ) -> tuple[Optional[_Candidate], list[_Candidate], bool]:
        """在某车型上下文下选最优候选。返回 (top, sorted_all, has_conflict)"""
        all_cands: list[_Candidate] = []
        for rule in candidates:
            policy = policy_map.get(rule.policy_id)
            if not policy:
                continue
            all_cands.extend(CostMatcher._build_candidates_for_rule(
                rule, policy, ctx, vehicle, region_level_cache,
            ))
        if not all_cands:
            return None, [], False

        all_cands.sort(key=lambda c: (
            -c.score,
            c.rule.price_type,
            -(c.rule.rule_version or 1),
            -c.rule.id,
        ))
        top = all_cands[0]
        ties = [
            c for c in all_cands
            if c.score == top.score and c.rule.id != top.rule.id
            and c.rule.price_type == top.rule.price_type
            and (c.rule.rule_version or 1) == (top.rule.rule_version or 1)
        ]
        return top, all_cands, bool(ties)

    # ---------- 公共入口 ----------

    @staticmethod
    def match_fee_type(
        fee_type: str,
        candidates: list[CostRule],
        policy_map: dict[int, CostPolicy],
        ctx: TaskCostContext,
        region_level_cache: dict[int, str],
    ) -> list[FeeItemResult]:
        """对单个费用类型匹配并计算，返回一个或多个费用明细行。"""
        base_trace = {
            "engine": COST_ENGINE_VERSION,
            "fee_type": fee_type,
            "carrier_type": ctx.carrier_type,
            "origin_input": {
                "region_id": ctx.origin.region_id,
                "name": ctx.origin.region_name,
                "level": REGION_LEVEL_LABEL.get(ctx.origin.level or 0, "custom")
                if ctx.origin.region_id else None,
            },
            "destination_input": {
                "region_id": ctx.destination.region_id,
                "name": ctx.destination.region_name,
                "level": REGION_LEVEL_LABEL.get(ctx.destination.level or 0, "custom")
                if ctx.destination.region_id else None,
            },
        }

        if not candidates:
            if fee_type_is_required(fee_type):
                return [FeeItemResult(
                    fee_type=fee_type, fee_name=fee_type_name(fee_type),
                    error_type=ERR_RULE_NOT_FOUND,
                    error_message=f"必算费用项[{fee_type_name(fee_type)}]未匹配到规则",
                    match_trace={**base_trace, "candidate_count": 0},
                )]
            return []

        groups = ctx.vehicle_groups or [
            VehicleGroup(
                vehicle=VehicleResolution(
                    brand_id=None, series_id=None, brand_name=None,
                    series_name=None, matched_by="general",
                ),
                quantity=int(ctx.total_quantity or 0),
            )
        ]

        # 为每个车型组选最优规则；按 rule_id 聚合台数
        per_rule: dict[int, dict] = {}
        conflict = False
        matched_any = False
        for g in groups:
            top, all_cands, has_conflict = CostMatcher._select_best(
                candidates, policy_map, ctx, g.vehicle, region_level_cache,
            )
            if top is None:
                continue
            matched_any = True
            if has_conflict:
                conflict = True
            entry = per_rule.setdefault(top.rule.id, {
                "cand": top, "qty": 0, "top_candidates": all_cands[:5],
            })
            entry["qty"] += int(g.quantity or 0)

        if conflict:
            return [FeeItemResult(
                fee_type=fee_type, fee_name=fee_type_name(fee_type),
                error_type=ERR_RULE_CONFLICT,
                error_message=f"费用项[{fee_type_name(fee_type)}]匹配到多条同优先级规则",
                match_trace={**base_trace, "conflict": True},
            )]

        if not matched_any:
            if fee_type_is_required(fee_type):
                return [FeeItemResult(
                    fee_type=fee_type, fee_name=fee_type_name(fee_type),
                    error_type=ERR_RULE_NOT_FOUND,
                    error_message=f"必算费用项[{fee_type_name(fee_type)}]未匹配到规则",
                    match_trace={**base_trace, "candidate_count": len(candidates)},
                )]
            return []

        # 非台数计价方式：全任务只算一次（取得分最高的规则）
        first_cand: _Candidate = next(iter(per_rule.values()))["cand"]
        is_qty_method = first_cand.rule.pricing_method in QTY_METHODS

        results: list[FeeItemResult] = []
        if not is_qty_method:
            # 选所有命中规则里得分最高者，qty 用总台数
            best_rid = max(
                per_rule.keys(),
                key=lambda rid: per_rule[rid]["cand"].score,
            )
            entry = per_rule[best_rid]
            results.append(CostMatcher._make_item(
                fee_type, entry["cand"], ctx,
                qty=Decimal(str(ctx.total_quantity or 0)),
                base_trace=base_trace, top_candidates=entry["top_candidates"],
            ))
        else:
            # 台数计价：每条命中规则一行，qty 为其聚合台数
            for rid, entry in per_rule.items():
                cand = entry["cand"]
                qty = Decimal(str(entry["qty"] or 0))
                if qty <= 0:
                    item = FeeItemResult(
                        fee_type=fee_type, fee_name=fee_type_name(fee_type),
                        direction=cand.rule.direction,
                        payee_type=cand.rule.payee_type,
                        pricing_method=cand.rule.pricing_method,
                        matched_policy_id=cand.policy.id,
                        matched_rule_id=cand.rule.id,
                        matched_rule_version=cand.rule.rule_version,
                        match_score=cand.score,
                        error_type=ERR_INVALID_QTY,
                        error_message="台数为空或非正",
                        match_trace={**base_trace},
                    )
                    results.append(item)
                    continue
                results.append(CostMatcher._make_item(
                    fee_type, cand, ctx, qty=qty,
                    base_trace=base_trace, top_candidates=entry["top_candidates"],
                ))
        return results

    @staticmethod
    def _make_item(
        fee_type: str,
        cand: _Candidate,
        ctx: TaskCostContext,
        qty: Decimal,
        base_trace: dict,
        top_candidates: list[_Candidate],
    ) -> FeeItemResult:
        rule = cand.rule
        amount, used_qty, used_km, err = CostMatcher._calc_amount(rule, ctx, qty)
        trace = {
            **base_trace,
            "scope_matched": cand.scope_matched,
            "direction_match": cand.direction,
            "model_match_type": cand.model_match_type,
            "matched_origin": cand.origin_match_region_id,
            "matched_destination": cand.destination_match_region_id,
            "pricing_method": rule.pricing_method,
            "distance_source": (
                "rule" if rule.distance_km is not None else ctx.distance_source
            ) if rule.pricing_method in KM_METHODS else None,
            "score": cand.score,
            "score_breakdown": cand.score_breakdown,
            "top_candidates": [
                {"rule_id": c.rule.id, "score": c.score} for c in top_candidates
            ],
        }
        item = FeeItemResult(
            fee_type=fee_type,
            fee_name=rule.fee_name or fee_type_name(fee_type),
            direction=rule.direction,
            payee_type=rule.payee_type,
            pricing_method=rule.pricing_method,
            unit_price=rule.unit_price,
            matched_policy_id=cand.policy.id,
            matched_rule_id=rule.id,
            matched_rule_version=rule.rule_version,
            match_score=cand.score,
            match_trace=trace,
        )
        if err:
            item.error_type = err
            item.error_message = (
                "每公里/每吨公里缺少里程" if err == ERR_DISTANCE_NOT_FOUND else err
            )
            return item
        item.amount = amount or Decimal("0")
        item.quantity = used_qty
        item.distance_km = used_km
        return item
