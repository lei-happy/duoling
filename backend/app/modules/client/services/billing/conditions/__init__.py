"""
成本条件规则引擎（可插拔条件类型 + AND/OR 条件树）

设计目标：
  - 规则条件以 JSON 条件树存储（分组 {logic, children} 或 叶子 {type, op, value, ...}），
    加一种新条件类型 = 新增一个 evaluator + 注册，零改表、零迁移。
  - 每种条件类型是一个可插拔评估器：自带匹配逻辑 + 特异度评分 + 前端元数据。
  - 复用收入侧行政区/车型层级评分口径，保证存量规则命中与分数不变。

导入本包即完成内置评估器注册（见 evaluators.py 末尾的副作用注册）。
"""

from app.modules.client.services.billing.conditions.base import (
    ConditionEvaluator,
    ConditionMatch,
)
from app.modules.client.services.billing.conditions.registry import (
    CONDITION_REGISTRY,
    collect_leaf_types,
    describe_all,
    evaluate_tree,
    get_evaluator,
    register,
)

# 触发内置评估器注册（副作用导入）
from app.modules.client.services.billing.conditions import evaluators as _evaluators  # noqa: E402,F401

__all__ = [
    "ConditionEvaluator",
    "ConditionMatch",
    "CONDITION_REGISTRY",
    "collect_leaf_types",
    "describe_all",
    "evaluate_tree",
    "get_evaluator",
    "register",
]
