"""任务级费用单「发起节点」配置规则

用途：租户可配置「在哪些任务节点允许发起哪类费用单」。
- 配置真源：``biz_system_config`` 键 ``finance.task_doc_stage_rules``（JSON，租户级）。
- 消费方：
  1. 前端入口显隐 / docType 下拉过滤（始终按 ``rules`` 生效，作为业务引导）；
  2. 后端 ``TaskFinanceService.create_doc`` 校验（仅当 ``enforce=true`` 时硬拦截，
     否则仅记录警告日志，保持财务与 ``task.status`` 的弱联动约定）。

设计原则：默认「全节点放开 + 不强制拦截」，升级后行为与现状完全一致；
租户按需在「系统设置 → 财务设置」中收紧。
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple

from app.modules.client.services.finance.base.constants import DocType
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_STATUS_LABELS,
)

logger = logging.getLogger(__name__)

# ``biz_system_config`` 约定
STAGE_RULES_CONFIG_KEY = "finance.task_doc_stage_rules"
STAGE_RULES_CONFIG_GROUP = "finance"
STAGE_RULES_DESCRIPTION = (
    "费用单发起节点规则 JSON：enforce 是否强制拦截；"
    "rules 为「单据类型→允许发起的任务节点集合」"
)

# 单据类型中文名（用于用户可读的拦截提示）
DOC_TYPE_LABELS: Dict[int, str] = {
    DocType.PREPAY: "预付单",
    DocType.SUPPLEMENT: "补款单",
    DocType.SETTLE: "结算单",
    DocType.CONTRACTED: "承包单",
}

# 全部任务节点（含 -1 待分配 … 9 已取消），默认全部放开
ALL_TASK_STATUSES: List[int] = sorted(TASK_STATUS_LABELS.keys())


def default_rules() -> Dict[int, List[int]]:
    """默认规则：每种单据类型在所有节点均可发起。"""
    return {dt: list(ALL_TASK_STATUSES) for dt in DocType.ALL}


def default_stage_rules_json() -> str:
    """默认配置 JSON（供开户种子 / 懒补齐使用）。"""
    return json.dumps(
        {"enforce": False, "rules": {str(k): v for k, v in default_rules().items()}},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def parse_stage_rules(
    config_value: Optional[str],
) -> Tuple[bool, Dict[int, Set[int]]]:
    """解析配置值，返回 ``(enforce, rules)``。

    - 配置缺失 / 解析失败 → 回退默认（全放开、不拦截），保证向后兼容；
    - 缺失的单据类型 → 该类型视为全放开。
    """
    enforce = False
    rules: Dict[int, Set[int]] = {dt: set(ALL_TASK_STATUSES) for dt in DocType.ALL}
    if not config_value:
        return enforce, rules
    try:
        obj = json.loads(config_value)
        enforce = bool(obj.get("enforce", False))
        raw = obj.get("rules") or {}
        for key, statuses in raw.items():
            try:
                dt = int(key)
            except (TypeError, ValueError):
                continue
            if dt in DocType.ALL and isinstance(statuses, list):
                rules[dt] = {int(s) for s in statuses}
    except (ValueError, TypeError, AttributeError):
        logger.warning("费用单发起节点规则解析失败，回退默认全放开: %r", config_value)
        return False, {dt: set(ALL_TASK_STATUSES) for dt in DocType.ALL}
    return enforce, rules


def creatable_doc_types(
    task_status: int,
    rules: Dict[int, Set[int]],
) -> List[int]:
    """给定任务节点，返回当前允许发起的单据类型（按 DocType.ALL 顺序）。"""
    return [dt for dt in DocType.ALL if task_status in rules.get(dt, set())]


def assert_stage_allowed(
    doc_type: int,
    task_status: int,
    enforce: bool,
    rules: Dict[int, Set[int]],
) -> None:
    """校验当前节点是否允许发起该类单据。

    - ``enforce=True`` 且不允许 → 抛业务异常（用户可读文案）；
    - ``enforce=False`` 且不允许 → 仅记录警告日志，放行（软提示模式）。
    """
    allowed = task_status in rules.get(doc_type, set(ALL_TASK_STATUSES))
    if allowed:
        return
    status_label = TASK_STATUS_LABELS.get(task_status, "当前状态")
    doc_label = DOC_TYPE_LABELS.get(doc_type, "该费用单")
    if enforce:
        from app.common.exceptions import BizException

        raise BizException(f"当前任务处于「{status_label}」，暂不能发起{doc_label}")
    logger.info(
        "费用单发起节点软提示：任务节点=%s 不在 %s 的允许集合内（未强制拦截）",
        status_label,
        doc_label,
    )
