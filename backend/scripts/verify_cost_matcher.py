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

print(f"\n==== 结果：{passed} 通过 / {failed} 失败 ====")
if failed:
    raise SystemExit(1)
