"""审批中心 - 条件表达式求值

第 1 期支持单层 and/or + 比较运算的 JSON DSL：

    {
      "logic": "and",
      "rules": [
        {"field": "amount", "op": ">=", "value": 10000},
        {"field": "doc_type", "op": "in", "value": [3, 9]}
      ]
    }

空条件视为恒真。详见《08.审批中心/01.审批引擎核心设计》§七。
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def _cmp(left: Any, op: str, right: Any) -> bool:
    try:
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "in":
            return left in (right or [])
        if op == "not_in":
            return left not in (right or [])
        # 数值比较，尽量转成 float 容错
        if op in (">", ">=", "<", "<="):
            lf = float(left)
            rf = float(right)
            if op == ">":
                return lf > rf
            if op == ">=":
                return lf >= rf
            if op == "<":
                return lf < rf
            if op == "<=":
                return lf <= rf
    except (TypeError, ValueError):
        return False
    return False


def eval_condition(
    condition: Optional[Dict[str, Any]],
    variables: Optional[Dict[str, Any]],
) -> bool:
    """求值条件；空条件恒真。"""
    if not condition:
        return True
    rules = condition.get("rules") or []
    if not rules:
        return True
    variables = variables or {}
    logic = (condition.get("logic") or "and").lower()
    results = []
    for rule in rules:
        field = rule.get("field")
        op = rule.get("op")
        value = rule.get("value")
        results.append(_cmp(variables.get(field), op, value))
    if logic == "or":
        return any(results)
    return all(results)
