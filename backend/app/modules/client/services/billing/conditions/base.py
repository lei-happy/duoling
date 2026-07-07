"""
条件评估器基类与匹配结果结构。

约定：
  - 叶子节点结构：{"type": <条件类型key>, "op": <操作符>, "value": <值>, "negate": bool, ...}
  - 分组节点结构：{"logic": "and"|"or", "children": [<node>, ...]}
  - Evaluator.evaluate 返回 None 表示"该条件不满足"→ 规则被淘汰；
    返回 ConditionMatch 表示满足，附带特异度评分与可读 trace。
  - facts 用于向匹配器透出命中细节（方向/命中行政区/车型层级等），
    经 AND 合并 / OR 取胜方后由 CostMatcher 还原候选的 trace 字段与"维度默认分"。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ConditionMatch:
    """单个条件（或子树）命中结果。"""

    score_delta: int = 0
    # 命中事实（供匹配器还原 direction / model_match_type / 命中行政区等）：
    #   line_matched: bool         region_route 命中线路（占据"线路维度"）
    #   direction / matched_origin / matched_destination / origin_level / destination_level
    #   model_match_type: str      vehicle_brand/series 命中（占据"车型维度"）
    facts: dict = field(default_factory=dict)
    # 可读 trace 片段（列表，便于 AND 累积）
    trace: list = field(default_factory=list)


class ConditionEvaluator:
    """条件类型评估器抽象基类。子类需定义 key 并实现 evaluate。"""

    key: str = ""
    label: str = ""
    # 前端值组件类型：text / number / number_range / region / region_route
    #   / brand / series / enum / carrier / capacity / enterprise / driver
    value_type: str = "text"
    operators: list[str] = ["eq"]
    # 前端选项来源（下拉/级联数据源标识），无则 None
    option_source: Optional[str] = None
    # 可选字段候选（如 text_contains 的 origin_name/destination_name）
    fields: Optional[list[dict]] = None

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        raise NotImplementedError

    def describe(self) -> dict:
        d = {
            "key": self.key,
            "label": self.label,
            "valueType": self.value_type,
            "operators": list(self.operators),
            "optionSource": self.option_source,
        }
        if self.fields:
            d["fields"] = self.fields
        return d


# ---- 通用比较辅助 ----

def _to_number(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def compare_scalar(actual: Any, op: str, value: Any) -> bool:
    """标量/区间通用比较。op ∈ eq/ne/in/nin/contains/gte/lte/gt/lt/between。"""
    op = (op or "eq").lower()

    if op == "eq":
        return _loose_eq(actual, value)
    if op == "ne":
        return not _loose_eq(actual, value)
    if op == "in":
        seq = value if isinstance(value, (list, tuple, set)) else [value]
        return any(_loose_eq(actual, v) for v in seq)
    if op == "nin":
        seq = value if isinstance(value, (list, tuple, set)) else [value]
        return not any(_loose_eq(actual, v) for v in seq)
    if op == "contains":
        if actual is None or value is None:
            return False
        return str(value) in str(actual)

    # 数值比较
    a = _to_number(actual)
    if a is None:
        return False
    if op == "between":
        if not isinstance(value, (list, tuple)) or len(value) < 2:
            return False
        lo, hi = _to_number(value[0]), _to_number(value[1])
        if lo is not None and a < lo:
            return False
        if hi is not None and a > hi:
            return False
        return True
    b = _to_number(value)
    if b is None:
        return False
    if op == "gte":
        return a >= b
    if op == "lte":
        return a <= b
    if op == "gt":
        return a > b
    if op == "lt":
        return a < b
    return False


def _loose_eq(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == bool(b)
    # 数字宽松相等（"1"==1）
    na, nb = _to_number(a), _to_number(b)
    if na is not None and nb is not None:
        return na == nb
    return str(a) == str(b)
