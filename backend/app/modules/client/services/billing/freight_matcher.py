"""
运费匹配引擎（计费引擎 Phase 2 - 纯算法层）

设计要点：
  - 纯算法：所有数据加载由编排层（FreightCalcService）提前完成，
    本类只接受标准化后的输入，不直接访问 DB。
  - 综合评分：客户分 + 线路分（按层级）+ 车型分（按层级）+ 方向分
    + 版本分 + 人工 priority。最高分唯一即命中，否则进入冲突。
  - 反向线路：仅当 rule.is_bidirectional=1 时才允许；反向比正向低 200 分。
  - match_trace：完整记录候选集合 / 命中维度 / 评分明细，便于审计与回放。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from app.modules.client.models.billing.freight_contract import FreightContract
from app.modules.client.models.billing.freight_rate import FreightRate
from app.modules.client.services.billing.standardize_service import (
    REGION_LEVEL_LABEL,
    RegionResolution,
    VehicleResolution,
)


CALC_ENGINE_VERSION = "v2.0.0"


# ---- 评分权重（按设计文档 8.6 实现 + 项目特化）----

CUSTOMER_SCORE = 100_000

# 线路层级：dist=district / city / province
LINE_SCORE = {
    ("district", "district"): 30_000,
    ("district", "city"): 25_000,
    ("city", "district"): 25_000,
    ("city", "city"): 20_000,
    ("province", "city"): 15_000,
    ("city", "province"): 15_000,
    ("province", "province"): 10_000,
    # custom 视为最弱（与省级同级）
    ("custom", "custom"): 8_000,
}

# 车型层级
MODEL_SCORE = {
    "series": 3_000,
    "brand": 2_000,
    "general": 1_000,
}

# 方向加分
DIR_SCORE = {
    "forward": 500,
    "backward": 300,
}

# 价格类型：明确价 +200，预估价 0
PRICE_TYPE_SCORE = {0: 200, 1: 0}

# 版本号：每个版本+1（用于细微优先级）
VERSION_BONUS_PER = 1


# ---- 异常类型 ----

ERR_AREA_NOT_RECOGNIZED = "AREA_NOT_RECOGNIZED"
ERR_SERIES_NOT_RECOGNIZED = "SERIES_NOT_RECOGNIZED"
ERR_CONTRACT_NOT_FOUND = "CONTRACT_NOT_FOUND"
ERR_RULE_NOT_FOUND = "RULE_NOT_FOUND"
ERR_RULE_CONFLICT = "RULE_CONFLICT"
ERR_INVALID_QTY = "INVALID_QTY"


# ---- 数据结构 ----


@dataclass
class CargoInput:
    """单条货物明细的匹配输入"""

    waybill_cargo_id: int
    quantity: int
    vehicle: VehicleResolution


@dataclass
class WaybillContext:
    """运单级别的匹配上下文"""

    customer_id: int
    transport_date: date
    origin: RegionResolution
    destination: RegionResolution


@dataclass
class CandidateRule:
    """评分候选（一条 rule 在某个方向 + 某个线路层级 + 某个车型层级 下的一个候选）"""

    rule: FreightRate
    contract: FreightContract
    direction: str  # forward / backward
    origin_match_level: str
    destination_match_level: str
    origin_match_region_id: int
    destination_match_region_id: int
    model_match_type: str  # series / brand / general
    score: int
    score_breakdown: dict


@dataclass
class CargoMatchResult:
    """单条货物明细的匹配结果"""

    waybill_cargo_id: int

    # 命中（success）
    matched_rule: Optional[FreightRate] = None
    matched_contract: Optional[FreightContract] = None
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

    # 异常（calc_status=exception）
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    match_trace: dict = field(default_factory=dict)

    @property
    def calc_status(self) -> str:
        return "exception" if self.error_type else "success"


# ---- 算法 ----


class FreightMatcher:

    @staticmethod
    def _calc_amount(rule: FreightRate, quantity: int) -> Decimal:
        """按计费模式计算单条明细的金额；min_amount 兜底。"""
        unit = rule.unit_price or Decimal("0")
        if rule.billing_mode == 1:
            km = rule.distance_km or Decimal("0")
            total = unit * km * quantity
        elif rule.billing_mode == 2:
            # 整单价：与设计方案一致——本期约定整单价规则只允许单货物明细命中
            # 多明细命中时由编排层做"按 quantity 加权"分摊，本算法层只算原值
            total = unit
        else:
            total = unit * quantity
        if rule.min_amount is not None and total < rule.min_amount:
            total = rule.min_amount
        return total

    # ---- 候选集合构造 ----

    @staticmethod
    def _origin_candidate_region_ids(ctx: WaybillContext) -> list[tuple[int, str]]:
        """运单出发地按 region 树自下而上展开，返回 [(region_id, level_label)]"""
        return [(n.region_id, n.level_label) for n in ctx.origin.chain]

    @staticmethod
    def _destination_candidate_region_ids(ctx: WaybillContext) -> list[tuple[int, str]]:
        return [(n.region_id, n.level_label) for n in ctx.destination.chain]

    @staticmethod
    def _resolve_rule_levels(rule: FreightRate, region_resolution_cache: dict[int, str]) -> tuple[str, str]:
        """获取规则两端的 level_label。

        region_resolution_cache: rule.origin_region_id / destination_region_id → level_label
        若缓存未命中（rule 未标准化），用 'custom' 兜底。
        """
        ol = region_resolution_cache.get(rule.origin_region_id, "custom")
        dl = region_resolution_cache.get(rule.destination_region_id, "custom")
        return ol, dl

    @staticmethod
    def _model_match_type(rule: FreightRate, vehicle: VehicleResolution) -> Optional[str]:
        """判断本条 rule 在给定车型解析下能命中哪一级（None 表示该 rule 在车型维度上不匹配）

        规则：
          - rule.series_id 非空：要求 vehicle.series_id 相等 → 'series'
          - rule.brand_id 非空且 series_id 为空：要求 vehicle.brand_id 相等 → 'brand'
          - rule.brand_id / series_id 都为空：通用 → 'general'
        """
        if rule.series_id is not None:
            if vehicle.series_id is not None and rule.series_id == vehicle.series_id:
                return "series"
            return None
        if rule.brand_id is not None:
            if vehicle.brand_id is not None and rule.brand_id == vehicle.brand_id:
                return "brand"
            return None
        return "general"

    @staticmethod
    def _direction_for(
        rule: FreightRate, oid: int, did: int
    ) -> Optional[str]:
        """判定该 rule 在出发地 oid / 目的地 did 下的方向。

        规则：
          - rule.origin_region_id == oid 且 destination_region_id == did → forward
          - 否则若 rule.is_bidirectional=1 且 origin_region_id == did 且
            destination_region_id == oid → backward
          - 其它返回 None（未命中线路）
        """
        if rule.origin_region_id == oid and rule.destination_region_id == did:
            return "forward"
        if (
            rule.is_bidirectional == 1
            and rule.origin_region_id == did
            and rule.destination_region_id == oid
        ):
            return "backward"
        return None

    @staticmethod
    def _build_candidates_for_rule(
        rule: FreightRate,
        contract: FreightContract,
        ctx: WaybillContext,
        cargo: CargoInput,
        region_level_cache: dict[int, str],
    ) -> list[CandidateRule]:
        """为单条 rule 在 ctx + cargo 下生成所有可能的命中候选"""
        out: list[CandidateRule] = []

        # 车型维度先粗过滤
        model_type = FreightMatcher._model_match_type(rule, cargo.vehicle)
        if model_type is None:
            return out

        # 线路维度：尝试每个 (origin_candidate, destination_candidate) 组合
        for oid, ol in FreightMatcher._origin_candidate_region_ids(ctx):
            for did, dl in FreightMatcher._destination_candidate_region_ids(ctx):
                direction = FreightMatcher._direction_for(rule, oid, did)
                if direction is None:
                    continue

                # 评分
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
                    CUSTOMER_SCORE
                    + line_s
                    + model_s
                    + dir_s
                    + price_type_s
                    + version_s
                    + (rule.priority or 0)
                )

                out.append(CandidateRule(
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
                        "customer": CUSTOMER_SCORE,
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
                # 一个 rule 对一个 (oid, did) 只产一个候选；外层继续穷举其它组合
        return out

    # ---- 公共入口 ----

    @staticmethod
    def match_one_cargo(
        ctx: WaybillContext,
        cargo: CargoInput,
        candidate_rules: list[FreightRate],
        contract_map: dict[int, FreightContract],
        region_level_cache: dict[int, str],
    ) -> CargoMatchResult:
        """对单条货物明细做匹配。

        前置：
          - candidate_rules 已按 customer_id + 状态生效 + 规则生效期 过滤
          - contract_map: contract_id → 已生效合同
          - region_level_cache: rule 所引用的所有 region_id → level_label
        """
        result = CargoMatchResult(waybill_cargo_id=cargo.waybill_cargo_id)
        trace: dict = {
            "engine": CALC_ENGINE_VERSION,
            "customer_id": ctx.customer_id,
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
                "matched_by": cargo.vehicle.matched_by,
                "brand_id": cargo.vehicle.brand_id,
                "series_id": cargo.vehicle.series_id,
                "brand_name": cargo.vehicle.brand_name,
                "series_name": cargo.vehicle.series_name,
            },
            "origin_chain": [
                {"region_id": rid, "level": lvl}
                for rid, lvl in FreightMatcher._origin_candidate_region_ids(ctx)
            ],
            "destination_chain": [
                {"region_id": rid, "level": lvl}
                for rid, lvl in FreightMatcher._destination_candidate_region_ids(ctx)
            ],
            "candidate_count": 0,
            "top_candidates": [],
        }
        result.match_trace = trace

        # 前置异常
        if cargo.quantity is None or cargo.quantity <= 0:
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
        all_cands: list[CandidateRule] = []
        for rule in candidate_rules:
            contract = contract_map.get(rule.contract_id)
            if not contract:
                continue
            cands = FreightMatcher._build_candidates_for_rule(
                rule, contract, ctx, cargo, region_level_cache,
            )
            all_cands.extend(cands)

        trace["candidate_count"] = len(all_cands)

        if not all_cands:
            # 区分两种"无规则"：规则全无 vs 车型识别不出
            if cargo.vehicle.matched_by == "unresolved" and not (
                cargo.vehicle.brand_id or cargo.vehicle.series_id
            ):
                result.error_type = ERR_SERIES_NOT_RECOGNIZED
                result.error_message = "无法识别车型"
            else:
                result.error_type = ERR_RULE_NOT_FOUND
                result.error_message = "未匹配到有效运价规则"
            return result

        # 按分数排序，最高分唯一才算命中
        all_cands.sort(key=lambda c: (
            -c.score,
            c.rule.price_type,        # 0(明确) 优先于 1(预估)
            -(c.rule.rule_version or 1),
            -c.rule.id,
        ))

        # 写入 top 5 候选用于审计
        trace["top_candidates"] = [
            {
                "rule_id": c.rule.id,
                "contract_id": c.contract.id,
                "score": c.score,
                "direction": c.direction,
                "origin_match_region_id": c.origin_match_region_id,
                "destination_match_region_id": c.destination_match_region_id,
                "origin_match_level": c.origin_match_level,
                "destination_match_level": c.destination_match_level,
                "model_match_type": c.model_match_type,
                "score_breakdown": c.score_breakdown,
            }
            for c in all_cands[:5]
        ]

        top = all_cands[0]
        # 多条同分时检测冲突：score 完全相同且 price_type、rule_version、id 都相同
        # 才算冲突；通常 id 不同，但 score 相同已经足够进入异常
        ties = [c for c in all_cands if c.score == top.score and c.rule.id != top.rule.id]
        if ties:
            # 进一步用 price_type / rule_version 自动消歧；都一致才算冲突
            still_tied = [
                c for c in ties
                if c.rule.price_type == top.rule.price_type
                and (c.rule.rule_version or 1) == (top.rule.rule_version or 1)
            ]
            if still_tied:
                result.error_type = ERR_RULE_CONFLICT
                tied_ids = [top.rule.id] + [c.rule.id for c in still_tied]
                result.error_message = f"匹配到多条同优先级规则: {tied_ids}"
                return result

        # 命中
        amount = FreightMatcher._calc_amount(top.rule, cargo.quantity)
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
