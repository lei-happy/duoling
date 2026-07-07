"""
成本引擎核心算法自检（纯内存，不连库）

覆盖设计文档 §17 部分用例：
  - 四种计价（per_vehicle / per_km / per_trip / fixed）
  - 多费用项汇总（加项 - 扣减项）
  - 每公里乘台数开关
  - 里程优先级（规则 distance_km > 线路）
  - 保底 / 封顶 / 取整
  - 必算项未匹配异常（driver_freight）
  - tiered / percentage
运行：cd backend && python -m scripts.verify_cost_matcher
"""

from decimal import Decimal

from app.modules.client.models.billing.cost_policy import CostPolicy
from app.modules.client.models.billing.cost_rule import CostRule
from app.modules.client.services.billing.cost_matcher import (
    CostMatcher,
    TaskCostContext,
    VehicleGroup,
)
from app.modules.client.services.billing.standardize_service import (
    RegionResolution,
    RegionNode,
    VehicleResolution,
)


def _region(rid, name, level, level_label):
    return RegionResolution(
        region_id=rid, region_code=str(rid), region_name=name,
        level=level, matched_by="id_input",
        chain=[RegionNode(region_id=rid, code=str(rid), name=name,
                          level=level, level_label=level_label)],
    )


def _policy(pid=1, scope_type=0, priority=0):
    p = CostPolicy(
        policy_no="P1", policy_name="默认", scope_type=scope_type,
        effective_date=None, status=1, priority=priority, version_no=1,
    )
    p.id = pid
    return p


def _rule(rid, fee_type, pricing_method, unit_price, **kw):
    r = CostRule(
        policy_id=1, fee_type=fee_type, pricing_method=pricing_method,
        unit_price=Decimal(str(unit_price)), direction=kw.get("direction", 1),
        payee_type=kw.get("payee_type", 1), multiply_by_qty=kw.get("multiply_by_qty", 0),
        round_mode=kw.get("round_mode", 0), price_type=0, priority=kw.get("priority", 0),
        rule_version=kw.get("rule_version", 1), is_bidirectional=0, status=1,
    )
    r.id = rid
    r.origin_region_id = kw.get("origin_region_id")
    r.destination_region_id = kw.get("destination_region_id")
    r.brand_id = kw.get("brand_id")
    r.series_id = kw.get("series_id")
    r.distance_km = (Decimal(str(kw["distance_km"])) if kw.get("distance_km") is not None else None)
    r.min_amount = (Decimal(str(kw["min_amount"])) if kw.get("min_amount") is not None else None)
    r.max_amount = (Decimal(str(kw["max_amount"])) if kw.get("max_amount") is not None else None)
    r.tiers_json = kw.get("tiers_json")
    r.percent_base = kw.get("percent_base")
    r.rate_percent = (Decimal(str(kw["rate_percent"])) if kw.get("rate_percent") is not None else None)
    r.fee_name = None
    return r


def _ctx(total_qty=5, distance_km=None, groups=None, freight_income=None):
    return TaskCostContext(
        carrier_type=1,
        transport_date=None,
        origin=_region(101, "A区", 3, "district"),
        destination=_region(202, "B区", 3, "district"),
        total_quantity=total_qty,
        vehicle_groups=groups or [],
        distance_km=(Decimal(str(distance_km)) if distance_km is not None else None),
        distance_source="biz_route" if distance_km is not None else None,
        freight_income=(Decimal(str(freight_income)) if freight_income is not None else None),
    )


passed = 0
failed = 0


def check(name, got, expect):
    global passed, failed
    ok = got == expect
    if ok:
        passed += 1
        print(f"[PASS] {name}: {got}")
    else:
        failed += 1
        print(f"[FAIL] {name}: got={got} expect={expect}")


policy_map = {1: _policy()}
cache = {}

# 1) per_vehicle: 5 台 * 200 = 1000
r = CostMatcher.match_fee_type(
    "driver_freight", [_rule(1, "driver_freight", "per_vehicle", 200)],
    policy_map, _ctx(total_qty=5), cache,
)
check("per_vehicle 总台数", r[0].amount, Decimal("1000.00"))

# 2) per_km 不乘台数: 3.5 * 100 = 350
r = CostMatcher.match_fee_type(
    "highway", [_rule(2, "highway", "per_km", 3.5)],
    policy_map, _ctx(distance_km=100), cache,
)
check("per_km 线路里程", r[0].amount, Decimal("350.00"))

# 3) per_km 规则里程优先 + 乘台数: 2 * 50 * 5 = 500
r = CostMatcher.match_fee_type(
    "fuel_subsidy",
    [_rule(3, "fuel_subsidy", "per_km", 2, distance_km=50, multiply_by_qty=1)],
    policy_map, _ctx(total_qty=5, distance_km=999), cache,
)
check("per_km 规则里程优先+乘台数", r[0].amount, Decimal("500.00"))

# 4) per_trip 固定
r = CostMatcher.match_fee_type(
    "loading", [_rule(4, "loading", "per_trip", 88)],
    policy_map, _ctx(total_qty=5), cache,
)
check("per_trip 固定", r[0].amount, Decimal("88.00"))

# 5) fixed 包车
r = CostMatcher.match_fee_type(
    "car_wash", [_rule(5, "car_wash", "fixed", 66)],
    policy_map, _ctx(total_qty=5), cache,
)
check("fixed 包车", r[0].amount, Decimal("66.00"))

# 6) per_km 缺里程 → 异常
r = CostMatcher.match_fee_type(
    "highway", [_rule(6, "highway", "per_km", 3.5)],
    policy_map, _ctx(distance_km=None), cache,
)
check("per_km 缺里程异常", r[0].error_type, "DISTANCE_NOT_FOUND")

# 7) 保底：3 台 * 10 = 30 < min 100 → 100
r = CostMatcher.match_fee_type(
    "loading", [_rule(7, "loading", "per_vehicle", 10, min_amount=100)],
    policy_map, _ctx(total_qty=3), cache,
)
check("保底金额", r[0].amount, Decimal("100.00"))

# 8) 封顶：10 台 * 100 = 1000 > max 500 → 500
r = CostMatcher.match_fee_type(
    "loading", [_rule(8, "loading", "per_vehicle", 100, max_amount=500)],
    policy_map, _ctx(total_qty=10), cache,
)
check("封顶金额", r[0].amount, Decimal("500.00"))

# 9) 取整（四舍五入到元）：3台 * 33.33 = 99.99 → 100
r = CostMatcher.match_fee_type(
    "other", [_rule(9, "other", "per_vehicle", 33.33, round_mode=1)],
    policy_map, _ctx(total_qty=3), cache,
)
check("四舍五入取整", r[0].amount, Decimal("100"))

# 10) 必算项无候选 → RULE_NOT_FOUND
r = CostMatcher.match_fee_type(
    "driver_freight", [], policy_map, _ctx(), cache,
)
check("必算项缺规则异常", r[0].error_type, "RULE_NOT_FOUND")

# 11) 可选项无候选 → 跳过（空列表）
r = CostMatcher.match_fee_type(
    "car_wash", [], policy_map, _ctx(), cache,
)
check("可选项缺规则跳过", len(r), 0)

# 12) tiered：前100台*5 + 后50台*4 = 500 + 200 = 700
tiers = [{"upTo": 100, "unitPrice": 5}, {"upTo": None, "unitPrice": 4}]
r = CostMatcher.match_fee_type(
    "driver_freight",
    [_rule(12, "driver_freight", "tiered", 0, tiers_json=tiers)],
    policy_map, _ctx(total_qty=150), cache,
)
check("阶梯累进", r[0].amount, Decimal("700.00"))

# 13) percentage：基数 10000 * 8% = 800
r = CostMatcher.match_fee_type(
    "driver_freight",
    [_rule(13, "driver_freight", "percentage", 0,
           percent_base="freight_income", rate_percent=8)],
    policy_map, _ctx(freight_income=10000), cache,
)
check("按比例", r[0].amount, Decimal("800.00"))

# 14) 多车型：限车系(series=9)规则 300/台 匹配2台 + 通用 100/台 由分组决定
g_series = VehicleGroup(
    vehicle=VehicleResolution(brand_id=1, series_id=9, brand_name=None,
                              series_name=None, matched_by="ids_input"),
    quantity=2,
)
g_other = VehicleGroup(
    vehicle=VehicleResolution(brand_id=2, series_id=8, brand_name=None,
                              series_name=None, matched_by="ids_input"),
    quantity=3,
)
rules = [
    _rule(14, "driver_freight", "per_vehicle", 300, series_id=9),
    _rule(15, "driver_freight", "per_vehicle", 100),
]
r = CostMatcher.match_fee_type(
    "driver_freight", rules, policy_map,
    _ctx(total_qty=5, groups=[g_series, g_other]), cache,
)
# series 组(2台*300=600) 命中规则14；other 组(3台*100=300) 命中规则15
amounts = sorted([it.amount for it in r])
check("多车型分组累加", amounts, [Decimal("300.00"), Decimal("600.00")])

# 15) 扣减项方向
r = CostMatcher.match_fee_type(
    "other", [_rule(16, "other", "fixed", 50, direction=2)],
    policy_map, _ctx(), cache,
)
check("扣减项方向", (r[0].direction, r[0].amount), (2, Decimal("50.00")))

# ============================================================
# 条件引擎 v2：新条件类型 / AND-OR 组合 / conditions_json 回归
# ============================================================

from types import SimpleNamespace  # noqa: E402


def _rule_cond(rid, fee_type, pricing_method, unit_price, conditions_json, **kw):
    r = _rule(rid, fee_type, pricing_method, unit_price, **kw)
    r.conditions_json = conditions_json
    return r


def _ctx_facts(total_qty=5, distance_km=None, groups=None, **facts):
    ctx = _ctx(total_qty=total_qty, distance_km=distance_km, groups=groups)
    for k, v in facts.items():
        setattr(ctx, k, v)
    return ctx


# 16) mileage_range between 命中：距离 150 ∈ [100,200] → per_vehicle 5*20=100
r = CostMatcher.match_fee_type(
    "highway",
    [_rule_cond(20, "highway", "per_vehicle", 20, {
        "logic": "and", "children": [
            {"type": "mileage_range", "op": "between", "value": [100, 200]},
        ],
    })],
    policy_map, _ctx_facts(total_qty=5, distance_km=150), cache,
)
check("里程区间命中", r[0].amount, Decimal("100.00"))

# 17) mileage_range 不命中：距离 300 ∉ [100,200] → 可选项跳过
r = CostMatcher.match_fee_type(
    "highway",
    [_rule_cond(21, "highway", "per_vehicle", 20, {
        "logic": "and", "children": [
            {"type": "mileage_range", "op": "between", "value": [100, 200]},
        ],
    })],
    policy_map, _ctx_facts(total_qty=5, distance_km=300), cache,
)
check("里程区间不命中跳过", len(r), 0)

# 18) text_contains 命中任务出发地名称（_ctx origin=A区）
r = CostMatcher.match_fee_type(
    "loading",
    [_rule_cond(22, "loading", "per_trip", 80, {
        "logic": "and", "children": [
            {"type": "text_contains", "field": "origin_name",
             "op": "contains", "value": "A区"},
        ],
    })],
    policy_map, _ctx_facts(total_qty=5), cache,
)
check("地名包含命中", r[0].amount, Decimal("80.00"))

# 19) AND 组合：里程命中 且 台数区间命中
r = CostMatcher.match_fee_type(
    "other",
    [_rule_cond(23, "other", "per_vehicle", 10, {
        "logic": "and", "children": [
            {"type": "mileage_range", "op": "gte", "value": 100},
            {"type": "quantity_range", "op": "between", "value": [1, 10]},
        ],
    })],
    policy_map, _ctx_facts(total_qty=5, distance_km=150), cache,
)
check("AND 组合命中", r[0].amount, Decimal("50.00"))

# 20) AND 组合部分不满足 → 淘汰（可选项跳过）
r = CostMatcher.match_fee_type(
    "other",
    [_rule_cond(24, "other", "per_vehicle", 10, {
        "logic": "and", "children": [
            {"type": "mileage_range", "op": "gte", "value": 100},
            {"type": "quantity_range", "op": "between", "value": [100, 200]},
        ],
    })],
    policy_map, _ctx_facts(total_qty=5, distance_km=150), cache,
)
check("AND 部分不满足淘汰", len(r), 0)

# 21) OR 组合：里程不满足 但 地名满足 → 命中
r = CostMatcher.match_fee_type(
    "other",
    [_rule_cond(25, "other", "per_trip", 66, {
        "logic": "or", "children": [
            {"type": "mileage_range", "op": "between", "value": [1, 10]},
            {"type": "text_contains", "field": "destination_name",
             "op": "contains", "value": "B区"},
        ],
    })],
    policy_map, _ctx_facts(total_qty=5, distance_km=150), cache,
)
check("OR 组合命中", r[0].amount, Decimal("66.00"))

# 22) 司机属性：结算模式=1（承包制）命中
drv_op = SimpleNamespace(settlement_mode=1, driver_type="A", department_id=7,
                         operation_status=1)
r = CostMatcher.match_fee_type(
    "driver_freight",
    [_rule_cond(26, "driver_freight", "per_vehicle", 120, {
        "logic": "and", "children": [
            {"type": "driver_attr", "field": "settlement_mode",
             "op": "eq", "value": 1},
        ],
    })],
    policy_map, _ctx_facts(total_qty=2, driver_operation=drv_op), cache,
)
check("司机属性命中", r[0].amount, Decimal("240.00"))

# 23) 车辆属性：车牌类型=NEW_ENERGY 命中
veh = SimpleNamespace(plate_category="NEW_ENERGY", status=1,
                      plate_number="", enterprise_id=None)
veh_ext = SimpleNamespace(vehicle_type="重型", load_capacity=Decimal("18.5"),
                          volume_capacity=None)
r = CostMatcher.match_fee_type(
    "fuel_subsidy",
    [_rule_cond(27, "fuel_subsidy", "per_trip", 30, {
        "logic": "and", "children": [
            {"type": "vehicle_attr", "field": "plate_category",
             "op": "eq", "value": "NEW_ENERGY"},
        ],
    })],
    policy_map,
    _ctx_facts(total_qty=2, transport_vehicle=veh, vehicle_ext=veh_ext),
    cache,
)
check("车辆属性命中", r[0].amount, Decimal("30.00"))

# 24) 车辆属性区间：核定载重 >=15 命中
r = CostMatcher.match_fee_type(
    "other",
    [_rule_cond(28, "other", "per_trip", 12, {
        "logic": "and", "children": [
            {"type": "vehicle_attr", "field": "load_capacity",
             "op": "gte", "value": 15},
        ],
    })],
    policy_map,
    _ctx_facts(total_qty=2, transport_vehicle=veh, vehicle_ext=veh_ext),
    cache,
)
check("车辆载重区间命中", r[0].amount, Decimal("12.00"))

# 25) negate：非承包制（settlement_mode != 1）时命中；当前=1 → 淘汰
r = CostMatcher.match_fee_type(
    "other",
    [_rule_cond(29, "other", "per_trip", 5, {
        "logic": "and", "children": [
            {"type": "driver_attr", "field": "settlement_mode",
             "op": "eq", "value": 1, "negate": True},
        ],
    })],
    policy_map, _ctx_facts(total_qty=2, driver_operation=drv_op), cache,
)
check("negate 取反淘汰", len(r), 0)

# 26) conditions_json 的 region_route 与 legacy 列同分（口径一致）
route_json = _rule_cond(30, "loading", "per_vehicle", 10, {
    "logic": "and", "children": [
        {"type": "region_route", "originRegionId": 101,
         "destinationRegionId": 202, "bidirectional": 0},
    ],
})
route_legacy = _rule(31, "loading", "per_vehicle", 10,
                     origin_region_id=101, destination_region_id=202)
cand_json = CostMatcher._build_candidate_for_rule(
    route_json, _policy(), _ctx_facts(total_qty=3),
    VehicleResolution(None, None, None, None, "general"), cache,
)
cand_legacy = CostMatcher._build_candidate_for_rule(
    route_legacy, _policy(), _ctx_facts(total_qty=3),
    VehicleResolution(None, None, None, None, "general"), cache,
)
check("conditions_json 与 legacy region_route 同分",
      cand_json.score, cand_legacy.score)

# 27) 空条件树（无约束）通用命中，与旧通用规则一致
cand_empty = CostMatcher._build_candidate_for_rule(
    _rule_cond(32, "loading", "per_vehicle", 10, {"logic": "and", "children": []}),
    _policy(), _ctx_facts(total_qty=3),
    VehicleResolution(None, None, None, None, "general"), cache,
)
cand_general = CostMatcher._build_candidate_for_rule(
    _rule(33, "loading", "per_vehicle", 10),
    _policy(), _ctx_facts(total_qty=3),
    VehicleResolution(None, None, None, None, "general"), cache,
)
check("空条件树与通用规则同分", cand_empty.score, cand_general.score)


print(f"\n==== 结果：{passed} 通过 / {failed} 失败 ====")
if failed:
    raise SystemExit(1)
