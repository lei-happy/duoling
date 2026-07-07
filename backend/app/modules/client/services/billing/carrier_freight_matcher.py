"""
承运商运费匹配引擎（承运运费引擎 - 纯算法层）

设计要点（与客户收入侧 FreightMatcher 对称，最大化复用其评分口径与谓词）：
  - 纯算法：所有数据加载由编排层（CarrierFreightCalcService）完成，本类只接受
    标准化后的输入，不直接访问 DB。
  - 计算粒度为「任务」：任务内按车型分组，逐组独立评分匹配并各自计算金额，
    汇总为整单承运运费。
  - 综合评分复用收入侧：线路分 / 车型分 / 方向分 / 价格类型分 + 版本 + 人工优先级，
    仅把最外层"客户分"替换为"承运商分"（CARRIER_SCORE）。
  - match_trace：完整记录候选集合 / 命中维度 / 评分明细，便于审计与回放。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from app.modules.client.models.billing.carrier_contract import CarrierContract
from app.modules.client.models.billing.carrier_rate import CarrierRate
from app.modules.client.services.billing.freight_matcher import (
    DIR_SCORE,
    ERR_AREA_NOT_RECOGNIZED,
    ERR_INVALID_QTY,
    ERR_RULE_CONFLICT,
    ERR_RULE_NOT_FOUND,
    ERR_SERIES_NOT_RECOGNIZED,
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


CARRIER_ENGINE_VERSION = "carrier-v1.0.0"

# 顶层"承运商分"，与收入侧"客户分"同量级
CARRIER_SCORE = 100_000


@dataclass
class CarrierContext:
    """任务级别的承运运费匹配上下文"""

    carrier_id: int
    transport_date: date
    origin: RegionResolution
    destination: RegionResolution


@dataclass
class VehicleGroupInput:
    """任务下按车型聚合的一组商品车"""

    quantity: int
    vehicle: VehicleResolution
    group_key: str = ""


@dataclass
class _Candidate:
    rule: CarrierRate
    contract: CarrierContract
    direction: str
    origin_match_level: str
    destination_match_level: str
    origin_match_region_id: int
    destination_match_region_id: int
    model_match_type: str
    score: int
    score_breakdown: dict


@dataclass
class GroupMatchResult:
    """单个车型分组的匹配结果"""

    group_key: str
    quantity: int
    brand_id: Optional[int] = None
    series_id: Optional[int] = None
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None

    matched_rule: Optional[CarrierRate] = None
    matched_contract: Optional[CarrierContract] = None
    direction: Optional[str] = None
    origin_match_level: Optional[str] = None
    destination_match_level: Optional[str] = None
    origin_match_region_id: Optional[int] = None
    destination_match_region_id: Optional[int] = None
    model_match_type: Optional[str] = None
    score: Optional[int] = None
    amount: Decimal = Decimal("0")
    unit_price: Optional[Decimal] = None
    billing_mode: Optional[int] = None
    distance_km: Optional[Decimal] = None

    error_type: Optional[str] = None
    error_message: Optional[str] = None

    match_trace: dict = field(default_factory=dict)

    @property
    def calc_status(self) -> str:
        return "exception" if self.error_type else "success"


class CarrierFreightMatcher:

    @staticmethod
    def _build_candidates_for_rule(
        rule: CarrierRate,
        contract: CarrierContract,
        ctx: CarrierContext,
        vehicle: VehicleResolution,
        region_level_cache: dict[int, str],
    ) -> list[_Candidate]:
        """为单条 rule 在 ctx + 车型下生成所有可能的命中候选（复用收入侧谓词）。"""
        out: list[_Candidate] = []

        model_type = FreightMatcher._model_match_type(rule, vehicle)
        if model_type is None:
            return out

        for oid, ol in [(n.region_id, n.level_label) for n in ctx.origin.chain]:
            for did, dl in [(n.region_id, n.level_label) for n in ctx.destination.chain]:
                direction = FreightMatcher._direction_for(rule, oid, did)
                if direction is None:
                    continue

                rule_o_level, rule_d_level = FreightMatcher._resolve_rule_levels(
                    rule, region_level_cache
                )
                line_key = (rule_o_level, rule_d_level)
                line_s = LINE_SCORE.get(line_key, 5_000)
                model_s = MODEL_SCORE.get(model_type, 0)
                dir_s = DIR_SCORE.get(direction, 0)
                price_type_s = PRICE_TYPE_SCORE.get(rule.price_type, 0)
                version_s = (rule.rule_version or 1) * VERSION_BONUS_PER

                total = (
                    CARRIER_SCORE + line_s + model_s + dir_s
                    + price_type_s + version_s + (rule.priority or 0)
                )

                out.append(_Candidate(
                    rule=rule,
                    contract=contract,
                    direction=direction,
                    origin_match_level=ol,
                    destination_match_level=dl,
                    origin_match_region_id=oid,
                    destination_match_region_id=did,
                    model_match_type=model_type,
                    score=total,
                    score_breakdown={
                        "carrier": CARRIER_SCORE,
                        "line": line_s,
                        "line_pair": f"{rule_o_level}->{rule_d_level}",
                        "model": model_s,
                        "model_layer": model_type,
                        "direction": dir_s,
                        "direction_label": direction,
                        "price_type": price_type_s,
                        "version": version_s,
                        "priority": (rule.priority or 0),
                    },
                ))
        return out

    @staticmethod
    def match_one_group(
        ctx: CarrierContext,
        group: VehicleGroupInput,
        candidate_rules: list[CarrierRate],
        contract_map: dict[int, CarrierContract],
        region_level_cache: dict[int, str],
    ) -> GroupMatchResult:
        """对单个车型分组做匹配（前置：candidate_rules 已按 carrier_id + 生效过滤）。"""
        vehicle = group.vehicle
        result = GroupMatchResult(
            group_key=group.group_key,
            quantity=group.quantity,
            brand_id=vehicle.brand_id,
            series_id=vehicle.series_id,
            vehicle_brand=vehicle.brand_name,
            vehicle_model=vehicle.series_name,
        )
        trace: dict = {
            "engine": CARRIER_ENGINE_VERSION,
            "carrier_id": ctx.carrier_id,
            "transport_date": ctx.transport_date.isoformat(),
            "origin_input": {
                "matched_by": ctx.origin.matched_by,
                "region_id": ctx.origin.region_id,
                "name": ctx.origin.region_name,
                "level": REGION_LEVEL_LABEL.get(ctx.origin.level or 0, "custom")
                if ctx.origin.region_id else None,
            },
            "destination_input": {
                "matched_by": ctx.destination.matched_by,
                "region_id": ctx.destination.region_id,
                "name": ctx.destination.region_name,
                "level": REGION_LEVEL_LABEL.get(ctx.destination.level or 0, "custom")
                if ctx.destination.region_id else None,
            },
            "vehicle_input": {
                "matched_by": vehicle.matched_by,
                "brand_id": vehicle.brand_id,
                "series_id": vehicle.series_id,
                "brand_name": vehicle.brand_name,
                "series_name": vehicle.series_name,
            },
            "candidate_count": 0,
            "top_candidates": [],
        }
        result.match_trace = trace

        # 前置异常
        if group.quantity is None or group.quantity <= 0:
            result.error_type = ERR_INVALID_QTY
            result.error_message = "台数为空或非正"
            return result
        if not ctx.origin.region_id or not ctx.destination.region_id:
            result.error_type = ERR_AREA_NOT_RECOGNIZED
            missing = []
            if not ctx.origin.region_id:
                missing.append("出发地")
            if not ctx.destination.region_id:
                missing.append("目的地")
            result.error_message = f"无法识别{','.join(missing)}的标准行政区"
            return result

        # 候选展开
        all_cands: list[_Candidate] = []
        for rule in candidate_rules:
            contract = contract_map.get(rule.contract_id)
            if not contract:
                continue
            all_cands.extend(CarrierFreightMatcher._build_candidates_for_rule(
                rule, contract, ctx, vehicle, region_level_cache,
            ))

        trace["candidate_count"] = len(all_cands)

        if not all_cands:
            if vehicle.matched_by == "unresolved" and not (
                vehicle.brand_id or vehicle.series_id
            ):
                result.error_type = ERR_SERIES_NOT_RECOGNIZED
                result.error_message = "无法识别车型"
            else:
                result.error_type = ERR_RULE_NOT_FOUND
                result.error_message = "未匹配到有效承运价规则"
            return result

        all_cands.sort(key=lambda c: (
            -c.score,
            c.rule.price_type,
            -(c.rule.rule_version or 1),
            -c.rule.id,
        ))

        trace["top_candidates"] = [
            {
                "rule_id": c.rule.id,
                "contract_id": c.contract.id,
                "score": c.score,
                "direction": c.direction,
                "origin_match_region_id": c.origin_match_region_id,
                "destination_match_region_id": c.destination_match_region_id,
                "model_match_type": c.model_match_type,
                "score_breakdown": c.score_breakdown,
            }
            for c in all_cands[:5]
        ]

        top = all_cands[0]
        ties = [c for c in all_cands if c.score == top.score and c.rule.id != top.rule.id]
        if ties:
            still_tied = [
                c for c in ties
                if c.rule.price_type == top.rule.price_type
                and (c.rule.rule_version or 1) == (top.rule.rule_version or 1)
            ]
            if still_tied:
                result.error_type = ERR_RULE_CONFLICT
                tied_ids = [top.rule.id] + [c.rule.id for c in still_tied]
                result.error_message = f"匹配到多条同优先级承运价规则: {tied_ids}"
                return result

        # 命中（金额计算复用收入侧 _calc_amount，口径与客户侧一致）
        amount = FreightMatcher._calc_amount(top.rule, group.quantity)
        result.matched_rule = top.rule
        result.matched_contract = top.contract
        result.direction = top.direction
        result.origin_match_level = top.origin_match_level
        result.destination_match_level = top.destination_match_level
        result.origin_match_region_id = top.origin_match_region_id
        result.destination_match_region_id = top.destination_match_region_id
        result.model_match_type = top.model_match_type
        result.score = top.score
        result.amount = amount
        result.unit_price = top.rule.unit_price
        result.billing_mode = top.rule.billing_mode
        result.distance_km = top.rule.distance_km
        return result
