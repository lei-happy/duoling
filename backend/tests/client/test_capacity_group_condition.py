"""计费引擎 · capacity_group 条件评估器（纯逻辑，零 DB）测试

覆盖运力分组接入成本规则条件引擎的判定语义：
  - 命中（eq / in）/ 不命中 / 空集淘汰 / value 缺省不约束
  - 特异度评分取 CONDITION_SCORE["capacity_group"]
  - 注册表与 describe 输出包含 capacity_group

对应需求：doc/02.需求文档/02.企业端/02.资源管理模块/05.运力分组.md
对应代码：backend/app/modules/client/services/billing/conditions/evaluators.py
覆盖用例：TC-CLI-CAPGROUP-030 ~ TC-CLI-CAPGROUP-037
"""

from __future__ import annotations

from types import SimpleNamespace

from app.modules.client.services.billing.conditions import evaluators  # noqa: F401
from app.modules.client.services.billing.conditions.registry import (
    CONDITION_REGISTRY,
    describe_all,
    evaluate_tree,
    get_evaluator,
)
from app.modules.client.services.billing.cost_constants import CONDITION_SCORE


def _ctx(**kw):
    base = dict(capacity_group_ids=set(), driver_id=None)
    base.update(kw)
    return SimpleNamespace(**base)


class TestCapacityGroupEvaluator:
    def test_registered(self):
        assert "capacity_group" in CONDITION_REGISTRY

    def test_eq_hit(self):
        ev = get_evaluator("capacity_group")
        m = ev.evaluate({"op": "eq", "value": 7}, _ctx(capacity_group_ids={7, 9}))
        assert m is not None
        assert m.score_delta == CONDITION_SCORE["capacity_group"]
        assert m.facts.get("capacity_group_matched") == 7

    def test_eq_miss(self):
        ev = get_evaluator("capacity_group")
        assert ev.evaluate(
            {"op": "eq", "value": 7}, _ctx(capacity_group_ids={1, 2})
        ) is None

    def test_in_hit_any(self):
        ev = get_evaluator("capacity_group")
        m = ev.evaluate(
            {"op": "in", "value": [3, 7, 12]}, _ctx(capacity_group_ids={9, 12})
        )
        assert m is not None
        assert m.facts.get("capacity_group_matched") == 12

    def test_string_value_coerced(self):
        ev = get_evaluator("capacity_group")
        m = ev.evaluate({"op": "eq", "value": "7"}, _ctx(capacity_group_ids={7}))
        assert m is not None

    def test_empty_group_set_eliminates(self):
        ev = get_evaluator("capacity_group")
        assert ev.evaluate({"op": "eq", "value": 7}, _ctx()) is None

    def test_value_missing_unconstrained(self):
        ev = get_evaluator("capacity_group")
        m = ev.evaluate({"op": "eq"}, _ctx(capacity_group_ids={7}))
        assert m is not None and m.score_delta == 0

    def test_score_between_capacity_and_driver(self):
        assert (
            CONDITION_SCORE["driver"]
            < CONDITION_SCORE["capacity_group"]
            < CONDITION_SCORE["capacity"]
        )

    def test_in_tree_and_combination(self):
        node = {"logic": "and", "children": [
            {"type": "capacity_group", "op": "eq", "value": 5},
            {"type": "driver", "op": "eq", "value": 100},
        ]}
        res = evaluate_tree(node, _ctx(capacity_group_ids={5}, driver_id=100))
        assert res is not None
        assert res.score_delta == (
            CONDITION_SCORE["capacity_group"] + CONDITION_SCORE["driver"]
        )

    def test_describe_includes_capacity_group(self):
        keys = {d["key"] for d in describe_all()}
        assert "capacity_group" in keys
