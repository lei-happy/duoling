"""
智能配载引擎（纯算法层）

设计要点（对齐 carrier_freight_matcher 的纯算法约定）：
  - 不访问 DB：所有数据由编排层（SmartStowageService）加载后以标准化结构传入。
  - 管线：召回/清洗 -> 线路聚类 -> 装箱(FFD) -> 多目标打分 -> Top-N 方案。
  - V1 采用规则 + 贪心 First-Fit-Decreasing，可解释；算法内部可无痛替换为
    元启发式 / 约束求解器（V2/V3）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.modules.client.services.task.smart_stowage.constants import (
    DEFAULT_MAX_PLANS,
    DEFAULT_MIN_LOAD_RATE,
    DEFAULT_TARGET_SPOTS,
    DEFAULT_WEIGHTS,
    resolve_occupy_coefficient,
)


@dataclass
class CargoCandidate:
    """算法输入：一条可配载的商品车候选行"""

    waybill_id: int
    waybill_cargo_id: int
    quantity: int
    waybill_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    vin: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None


@dataclass
class EngineParams:
    """算法参数"""

    target_spots: int = DEFAULT_TARGET_SPOTS
    occupy_overrides: dict[str, float] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    min_load_rate: float = DEFAULT_MIN_LOAD_RATE
    max_plans: int = DEFAULT_MAX_PLANS


@dataclass
class PlanItemResult:
    waybill_id: int
    waybill_cargo_id: int
    quantity: int
    occupy_coefficient: float
    waybill_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    vin: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None


@dataclass
class PlanResult:
    plan_no: int
    origin: Optional[str]
    destination: Optional[str]
    vehicle_count: int
    occupied_spots: float
    target_spots: int
    load_rate: float
    customer_count: int
    waybill_count: int
    score: float
    reason: str
    items: list[PlanItemResult]


def _norm(v: Optional[str]) -> str:
    return (v or "").strip()


class SmartStowageEngine:
    """智能配载引擎（无状态，静态方法）"""

    @staticmethod
    def generate(
        candidates: list[CargoCandidate],
        params: Optional[EngineParams] = None,
    ) -> list[PlanResult]:
        p = params or EngineParams()
        cap = max(1, int(p.target_spots))

        # ① 清洗 + 折算占位：展开为 per-台 单位（保留来源候选行引用）
        groups: dict[tuple[str, str], list[tuple[float, CargoCandidate]]] = {}
        for c in candidates:
            qty = max(0, int(c.quantity or 0))
            if qty <= 0:
                continue
            coef = resolve_occupy_coefficient(
                c.vehicle_model, c.vehicle_brand, p.occupy_overrides
            )
            key = (_norm(c.origin), _norm(c.destination))
            bucket = groups.setdefault(key, [])
            for _ in range(qty):
                bucket.append((coef, c))

        # ②③ 逐线路簇装箱
        raw_plans: list[PlanResult] = []
        for (origin, destination), units in groups.items():
            for bin_units in SmartStowageEngine._pack(units, cap):
                plan = SmartStowageEngine._build_plan(
                    origin, destination, bin_units, cap, p.weights
                )
                if plan is not None:
                    raw_plans.append(plan)

        # ④ 过滤低装载率 + 打分排序 + Top-N
        kept = [pl for pl in raw_plans if pl.load_rate >= p.min_load_rate]
        # 若全部被过滤（池子零散），保底返回评分最高的若干条
        if not kept and raw_plans:
            kept = raw_plans
        kept.sort(key=lambda x: x.score, reverse=True)
        kept = kept[: max(1, int(p.max_plans))]

        for idx, pl in enumerate(kept, start=1):
            pl.plan_no = idx
        return kept

    # ------------------------------------------------------------------
    # 装箱：First-Fit-Decreasing
    # ------------------------------------------------------------------
    @staticmethod
    def _pack(
        units: list[tuple[float, CargoCandidate]], cap: int
    ) -> list[list[tuple[float, CargoCandidate]]]:
        ordered = sorted(units, key=lambda x: -x[0])
        bins: list[dict] = []
        for coef, cand in ordered:
            placed = False
            for b in bins:
                if b["remaining"] + 1e-9 >= coef:
                    b["remaining"] -= coef
                    b["units"].append((coef, cand))
                    placed = True
                    break
            if not placed:
                bins.append({"remaining": cap - coef, "units": [(coef, cand)]})
        return [b["units"] for b in bins]

    # ------------------------------------------------------------------
    # 组装方案 + 打分
    # ------------------------------------------------------------------
    @staticmethod
    def _build_plan(
        origin: str,
        destination: str,
        bin_units: list[tuple[float, CargoCandidate]],
        cap: int,
        weights: dict[str, float],
    ) -> Optional[PlanResult]:
        if not bin_units:
            return None

        # 按 cargo 行聚合还原台数
        agg: dict[int, dict] = {}
        occupied = 0.0
        customers: set = set()
        waybills: set = set()
        for coef, cand in bin_units:
            occupied += coef
            waybills.add(cand.waybill_id)
            if cand.customer_id is not None:
                customers.add(cand.customer_id)
            row = agg.get(cand.waybill_cargo_id)
            if row is None:
                agg[cand.waybill_cargo_id] = {
                    "cand": cand,
                    "coef": coef,
                    "quantity": 1,
                }
            else:
                row["quantity"] += 1

        items = [
            PlanItemResult(
                waybill_id=r["cand"].waybill_id,
                waybill_cargo_id=cargo_id,
                quantity=r["quantity"],
                occupy_coefficient=r["coef"],
                waybill_no=r["cand"].waybill_no,
                customer_id=r["cand"].customer_id,
                customer_name=r["cand"].customer_name,
                vehicle_brand=r["cand"].vehicle_brand,
                vehicle_model=r["cand"].vehicle_model,
                vin=r["cand"].vin,
                origin=r["cand"].origin,
                destination=r["cand"].destination,
            )
            for cargo_id, r in agg.items()
        ]

        vehicle_count = sum(it.quantity for it in items)
        load_rate = min(100.0, round(occupied / cap * 100, 2)) if cap else 0.0
        customer_count = len(customers)
        waybill_count = len(waybills)

        # 多目标打分（均归一到 0-1）
        w = weights or DEFAULT_WEIGHTS
        s_load = load_rate / 100.0
        s_agg = min(1.0, vehicle_count / cap) if cap else 0.0
        s_conc = 1.0 / customer_count if customer_count > 0 else 1.0
        score = round(
            s_load * w.get("load_rate", 0.7)
            + s_agg * w.get("aggregation", 0.2)
            + s_conc * w.get("concentration", 0.1),
            4,
        )

        line = f"{origin or '未知'}→{destination or '未知'}"
        reason = (
            f"同线 {line} 聚合 {customer_count} 家客户 {waybill_count} 张运单共 "
            f"{vehicle_count} 台，车位利用率 {load_rate:.0f}%"
        )

        return PlanResult(
            plan_no=0,
            origin=origin or None,
            destination=destination or None,
            vehicle_count=vehicle_count,
            occupied_spots=round(occupied, 2),
            target_spots=cap,
            load_rate=load_rate,
            customer_count=customer_count,
            waybill_count=waybill_count,
            score=score,
            reason=reason,
            items=items,
        )
