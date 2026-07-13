"""计费引擎 · 条件引擎 v2（纯逻辑，零 DB）测试

覆盖：
  - 通用比较 ``compare_scalar`` / ``_loose_eq`` 全操作符矩阵
  - 条件树求值 ``evaluate_tree``（AND / OR / negate / 空树 / 未知类型）
  - 各内置 ``ConditionEvaluator`` 命中/不命中/不约束三态
  - 注册表 ``CONDITION_REGISTRY`` 完整性与 ``describe`` 结构

对应需求：doc/02.需求文档/02.企业端/05.计费引擎模块/**
对应代码：backend/app/modules/client/services/billing/conditions/**
覆盖用例：TC-CLI-BILLING-001 ~ TC-CLI-BILLING-040
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.modules.client.services.billing.conditions.base import (
    ConditionMatch,
    compare_scalar,
)
from app.modules.client.services.billing.conditions.registry import (
    CONDITION_REGISTRY,
    collect_leaf_types,
    describe_all,
    evaluate_tree,
    get_evaluator,
)
# 导入 evaluators 触发 @register 副作用（保证注册表非空）
from app.modules.client.services.billing.conditions import evaluators  # noqa: F401
from app.modules.client.services.billing.cost_constants import CONDITION_SCORE


# =====================================================================
# compare_scalar / _loose_eq
# =====================================================================
class TestCompareScalar:
    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, True), ("1", 1, True), (1, "1", True),
        ("abc", "abc", True), ("abc", "abd", False),
        (True, 1, True), (False, 0, True), (True, 0, False),
        (None, None, True), (None, 1, False),
    ])
    def test_eq(self, a, b, expected):
        assert compare_scalar(a, "eq", b) is expected

    def test_ne(self):
        assert compare_scalar("a", "ne", "b") is True
        assert compare_scalar(1, "ne", "1") is False

    def test_in_and_nin(self):
        assert compare_scalar(2, "in", [1, 2, 3]) is True
        assert compare_scalar(9, "in", [1, 2, 3]) is False
        assert compare_scalar(2, "in", 2) is True  # 标量自动包装
        assert compare_scalar(9, "nin", [1, 2, 3]) is True
        assert compare_scalar(2, "nin", [1, 2, 3]) is False

    def test_contains(self):
        assert compare_scalar("上海市浦东新区", "contains", "浦东") is True
        assert compare_scalar("北京", "contains", "上海") is False
        assert compare_scalar(None, "contains", "x") is False

    @pytest.mark.parametrize("op,val,expected", [
        ("gte", 10, True), ("gte", 20, False),
        ("lte", 20, True), ("lte", 5, False),
        ("gt", 10, True), ("gt", 15, False),
        ("lt", 20, True), ("lt", 15, False),
    ])
    def test_numeric_compare(self, op, val, expected):
        assert compare_scalar(15, op, val) is expected

    def test_between(self):
        assert compare_scalar(15, "between", [10, 20]) is True
        assert compare_scalar(25, "between", [10, 20]) is False
        assert compare_scalar(15, "between", [None, 20]) is True  # 开区间下界
        assert compare_scalar(15, "between", [10, None]) is True  # 开区间上界
        assert compare_scalar(15, "between", [10]) is False       # 非法区间

    def test_non_numeric_falls_false(self):
        assert compare_scalar("abc", "gte", 10) is False
        assert compare_scalar(10, "gte", "abc") is False

    def test_unknown_op_returns_false(self):
        assert compare_scalar(1, "weird", 1) is False


# =====================================================================
# evaluate_tree 结构语义
# =====================================================================
def _ctx(**kw):
    """构造一个最小 ctx（SimpleNamespace），未给的属性默认 None。"""
    base = dict(
        enterprise_id=None, carrier_id=None, carrier_type=None,
        capacity_id=None, driver_id=None, total_quantity=None,
        distance_km=None, origin=None, destination=None,
        dispatch_orders=None, current_vehicle=None,
        transport_vehicle=None, vehicle_ext=None,
        driver=None, driver_operation=None, region_level_cache=None,
    )
    base.update(kw)
    return SimpleNamespace(**base)


class TestEvaluateTree:
    def test_empty_tree_is_zero_match(self):
        res = evaluate_tree(None, _ctx())
        assert isinstance(res, ConditionMatch)
        assert res.score_delta == 0

    def test_empty_group_is_zero_match(self):
        res = evaluate_tree({"logic": "and", "children": []}, _ctx())
        assert res is not None
        assert res.score_delta == 0

    def test_and_all_hit(self):
        node = {"logic": "and", "children": [
            {"type": "enterprise", "op": "eq", "value": 7},
            {"type": "carrier", "op": "eq", "value": 3},
        ]}
        res = evaluate_tree(node, _ctx(enterprise_id=7, carrier_id=3))
        assert res is not None
        assert res.score_delta == (
            CONDITION_SCORE["enterprise"] + CONDITION_SCORE["carrier"]
        )

    def test_and_one_miss_eliminates(self):
        node = {"logic": "and", "children": [
            {"type": "enterprise", "op": "eq", "value": 7},
            {"type": "carrier", "op": "eq", "value": 3},
        ]}
        res = evaluate_tree(node, _ctx(enterprise_id=7, carrier_id=999))
        assert res is None

    def test_or_takes_best_branch(self):
        node = {"logic": "or", "children": [
            {"type": "enterprise", "op": "eq", "value": 7},  # 低分
            {"type": "carrier", "op": "eq", "value": 3},     # 高分
        ]}
        res = evaluate_tree(node, _ctx(enterprise_id=7, carrier_id=3))
        assert res is not None
        assert res.score_delta == CONDITION_SCORE["carrier"]

    def test_or_all_miss_eliminates(self):
        node = {"logic": "or", "children": [
            {"type": "enterprise", "op": "eq", "value": 7},
            {"type": "carrier", "op": "eq", "value": 3},
        ]}
        assert evaluate_tree(node, _ctx()) is None

    def test_negate_miss_becomes_zero_hit(self):
        node = {"type": "carrier", "op": "eq", "value": 3, "negate": True}
        res = evaluate_tree(node, _ctx(carrier_id=999))
        assert res is not None
        assert res.score_delta == 0

    def test_negate_hit_becomes_eliminated(self):
        node = {"type": "carrier", "op": "eq", "value": 3, "negate": True}
        assert evaluate_tree(node, _ctx(carrier_id=3)) is None

    def test_unknown_type_eliminates(self):
        assert evaluate_tree({"type": "no_such_cond", "value": 1}, _ctx()) is None

    def test_collect_leaf_types(self):
        node = {"logic": "and", "children": [
            {"type": "enterprise", "value": 1},
            {"logic": "or", "children": [
                {"type": "carrier", "value": 2},
                {"type": "driver", "value": 3},
            ]},
        ]}
        assert collect_leaf_types(node) == {"enterprise", "carrier", "driver"}


# =====================================================================
# 内置 evaluator 三态（命中 / 不命中 / 不约束）
# =====================================================================
class TestScalarEqEvaluators:
    @pytest.mark.parametrize("ctype,attr,score_key", [
        ("carrier", "carrier_id", "carrier"),
        ("capacity", "capacity_id", "capacity"),
        ("driver", "driver_id", "driver"),
        ("enterprise", "enterprise_id", "enterprise"),
        ("carrier_type", "carrier_type", "carrier_type"),
    ])
    def test_hit_miss_unconstrained(self, ctype, attr, score_key):
        ev = get_evaluator(ctype)
        # 命中
        m = ev.evaluate({"op": "eq", "value": 5}, _ctx(**{attr: 5}))
        assert m is not None and m.score_delta == CONDITION_SCORE[score_key]
        # 不命中
        assert ev.evaluate({"op": "eq", "value": 5}, _ctx(**{attr: 6})) is None
        # value 缺省 = 不约束（零分命中）
        m2 = ev.evaluate({"op": "eq"}, _ctx(**{attr: 5}))
        assert m2 is not None and m2.score_delta == 0


class TestVehicleModelEvaluators:
    def test_brand_hit(self):
        ev = get_evaluator("vehicle_brand")
        veh = SimpleNamespace(brand_id=10, series_id=None)
        m = ev.evaluate({"value": 10}, _ctx(current_vehicle=veh))
        assert m is not None
        assert m.facts.get("model_match_type") == "brand"

    def test_series_miss_when_vehicle_absent(self):
        ev = get_evaluator("vehicle_series")
        assert ev.evaluate({"value": 10}, _ctx(current_vehicle=None)) is None

    def test_unconstrained_when_value_missing(self):
        ev = get_evaluator("vehicle_brand")
        m = ev.evaluate({}, _ctx(current_vehicle=SimpleNamespace(brand_id=1)))
        assert m is not None and m.score_delta == 0


class TestRangeEvaluators:
    def test_mileage_from_distance(self):
        ev = get_evaluator("mileage_range")
        m = ev.evaluate({"op": "between", "value": [100, 300]},
                        _ctx(distance_km=200))
        assert m is not None and m.score_delta == CONDITION_SCORE["mileage_range"]

    def test_mileage_out_of_range(self):
        ev = get_evaluator("mileage_range")
        assert ev.evaluate({"op": "between", "value": [100, 150]},
                           _ctx(distance_km=200)) is None

    def test_mileage_actual_none(self):
        ev = get_evaluator("mileage_range")
        assert ev.evaluate({"op": "gte", "value": 1}, _ctx()) is None

    def test_quantity_range(self):
        ev = get_evaluator("quantity_range")
        m = ev.evaluate({"op": "gte", "value": 3}, _ctx(total_quantity=5))
        assert m is not None and m.score_delta == CONDITION_SCORE["quantity_range"]


class TestTextContainsEvaluator:
    def test_origin_name_contains(self):
        ev = get_evaluator("text_contains")
        origin = SimpleNamespace(region_name="上海市浦东新区")
        m = ev.evaluate(
            {"field": "origin_name", "op": "contains", "value": "浦东"},
            _ctx(origin=origin),
        )
        assert m is not None and m.score_delta == CONDITION_SCORE["text_contains"]

    def test_no_text_miss(self):
        ev = get_evaluator("text_contains")
        assert ev.evaluate(
            {"field": "origin_name", "value": "浦东"}, _ctx(origin=None)
        ) is None


class TestAttrEvaluators:
    def test_vehicle_attr_hit(self):
        ev = get_evaluator("vehicle_attr")
        veh = SimpleNamespace(plate_category="YELLOW", status=1,
                              plate_number="沪A", enterprise_id=1)
        m = ev.evaluate(
            {"field": "plate_category", "op": "eq", "value": "YELLOW"},
            _ctx(transport_vehicle=veh),
        )
        assert m is not None and m.score_delta == CONDITION_SCORE["vehicle_attr"]

    def test_vehicle_attr_field_missing_unconstrained(self):
        ev = get_evaluator("vehicle_attr")
        m = ev.evaluate({"value": "x"}, _ctx())  # 无 field → 不约束
        assert m is not None and m.score_delta == 0

    def test_driver_attr_hit(self):
        ev = get_evaluator("driver_attr")
        op = SimpleNamespace(settlement_mode=1, driver_type=2,
                             department_id=3, operation_status=1)
        m = ev.evaluate(
            {"field": "settlement_mode", "op": "eq", "value": 1},
            _ctx(driver_operation=op),
        )
        assert m is not None and m.score_delta == CONDITION_SCORE["driver_attr"]


class TestDispatchRouteEvaluator:
    def test_from_region_id_eq(self):
        ev = get_evaluator("dispatch_route")
        order = SimpleNamespace(from_region_id=110000, to_region_id=310000,
                                from_location="北京", to_location="上海",
                                mileage=1200)
        m = ev.evaluate(
            {"field": "from_region_id", "op": "eq", "value": 110000},
            _ctx(dispatch_orders=[order]),
        )
        assert m is not None and m.score_delta == CONDITION_SCORE["dispatch_route"]

    def test_no_orders_miss(self):
        ev = get_evaluator("dispatch_route")
        assert ev.evaluate(
            {"field": "from_region_id", "value": 1}, _ctx(dispatch_orders=[])
        ) is None


# =====================================================================
# 注册表完整性
# =====================================================================
class TestRegistry:
    def test_all_expected_keys_registered(self):
        expected = {
            "region_route", "vehicle_brand", "vehicle_series", "text_contains",
            "mileage_range", "quantity_range", "vehicle_attr", "driver_attr",
            "carrier", "carrier_type", "capacity", "driver", "enterprise",
            "dispatch_route",
        }
        assert expected <= set(CONDITION_REGISTRY.keys())

    def test_describe_shape(self):
        items = describe_all()
        assert len(items) == len(CONDITION_REGISTRY)
        for d in items:
            assert {"key", "label", "valueType", "operators", "optionSource"} <= set(d)
            assert isinstance(d["operators"], list)
