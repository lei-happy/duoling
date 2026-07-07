"""
条件类型注册表 + 条件树求值（AND / OR / negate）。

evaluate_tree 语义：
  - 分组 AND：所有子节点都命中才命中；分数累加；facts 合并（后者不覆盖已有"维度归属"键）。
  - 分组 OR ：任一子节点命中即命中；取分数最高的分支（其 facts / trace 生效）。
  - 叶子 negate：对结果取反（命中→淘汰；不命中→零分命中）。
  - 空树 / 空分组：视为"无条件约束"，命中且零分。
  - 未知条件类型：向前兼容失败保护，视为不命中（淘汰规则）。
"""

from __future__ import annotations

from typing import Any, Optional

from app.modules.client.services.billing.conditions.base import (
    ConditionEvaluator,
    ConditionMatch,
)

CONDITION_REGISTRY: dict[str, ConditionEvaluator] = {}


def register(cls):
    """类装饰器：实例化并按 key 注册到全局注册表。"""
    inst = cls()
    if not inst.key:
        raise ValueError(f"条件评估器缺少 key: {cls.__name__}")
    CONDITION_REGISTRY[inst.key] = inst
    return cls


def get_evaluator(key: str) -> Optional[ConditionEvaluator]:
    return CONDITION_REGISTRY.get(key)


def describe_all() -> list[dict]:
    return [ev.describe() for ev in CONDITION_REGISTRY.values()]


def _is_group(node: dict) -> bool:
    return bool(node) and ("children" in node or "logic" in node) and "type" not in node


def collect_leaf_types(node: Optional[dict]) -> set[str]:
    """收集条件树里出现的全部叶子条件类型（用于按需加载上下文 / 粗筛判断）。"""
    types: set[str] = set()
    if not node:
        return types
    if _is_group(node):
        for ch in node.get("children") or []:
            types |= collect_leaf_types(ch)
    elif node.get("type"):
        types.add(node["type"])
    return types


def _merge_facts(base: dict, extra: dict) -> None:
    for k, v in extra.items():
        base.setdefault(k, v)


def evaluate_tree(node: Optional[dict], ctx: Any) -> Optional[ConditionMatch]:
    """递归求值条件树。返回 None = 规则被淘汰。"""
    if not node:
        return ConditionMatch()

    if _is_group(node):
        logic = (node.get("logic") or "and").lower()
        children = node.get("children") or []
        if not children:
            return ConditionMatch()

        if logic == "or":
            best: Optional[ConditionMatch] = None
            for ch in children:
                res = evaluate_tree(ch, ctx)
                if res is None:
                    continue
                if best is None or res.score_delta > best.score_delta:
                    best = res
            return best  # None = 所有分支都不命中

        # AND
        total = 0
        facts: dict = {}
        traces: list = []
        for ch in children:
            res = evaluate_tree(ch, ctx)
            if res is None:
                return None
            total += res.score_delta
            _merge_facts(facts, res.facts)
            traces.extend(res.trace)
        return ConditionMatch(score_delta=total, facts=facts, trace=traces)

    # 叶子
    ctype = node.get("type")
    negate = bool(node.get("negate"))
    ev = CONDITION_REGISTRY.get(ctype)
    if ev is None:
        return None

    res = ev.evaluate(node, ctx)

    if negate:
        if res is None:
            return ConditionMatch(
                score_delta=0,
                trace=[{"type": ctype, "negate": True, "matched": True}],
            )
        return None

    return res
