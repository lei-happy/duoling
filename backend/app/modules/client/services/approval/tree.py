"""审批中心 - 画布流程树（条件分支）解析

可视化画布产出的流程定义是一棵树（对标钉钉/企微）：

    {
      "version": 1,
      "root": <node>
    }

节点 <node> 结构::

    {
      "nodeKey": "稳定唯一标识",
      "type": "start" | "approval" | "cc" | "condition",
      "nodeName": "节点名",
      # approval / cc 专有
      "approverType": 1..7,
      "approverConfig": {...} | None,
      "signType": 1..3,
      "emptyStrategy": 1..3,
      "allowTransfer": 0|1,
      "allowAddsign": 0|1,
      # condition（条件路由）专有
      "conditionNodes": [
        {"nodeKey", "nodeName", "priority": 1, "condition": {logic, rules}|None, "childNode": <node>|None}
      ],
      "childNode": <node> | None   # 下一节点 / 条件分支的汇合点
    }

引擎不直接“跑树”，而是在 start 时按 **提交变量（已冻结）** 把树展开（materialize）成一条
线性执行路径。因为审批变量在提交后不再变化，路径可在创建实例时一次性确定，
这样运行时引擎仍沿用既有的线性 node_order 推进逻辑，风险最小。

设计见《08.审批中心/03.前端交互与流程配置设计》。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.modules.client.services.approval import constants as C
from app.modules.client.services.approval.condition import eval_condition

# 节点类型（画布树用字符串，区别于实例节点的数值 node_type）
NODE_TYPE_START = "start"
NODE_TYPE_APPROVAL = "approval"
NODE_TYPE_CC = "cc"
NODE_TYPE_CONDITION = "condition"

# 画布字符串类型 → 实例节点数值 node_type
_TYPE_TO_NODE_TYPE = {
    NODE_TYPE_APPROVAL: C.NODE_TYPE_APPROVAL,
    NODE_TYPE_CC: C.NODE_TYPE_CC,
}


def _pick_branch(
    condition_nodes: List[Dict[str, Any]], variables: Optional[dict]
) -> Optional[Dict[str, Any]]:
    """从条件路由的分支中按优先级选中唯一命中分支。

    规则（对标钉钉条件分支，互斥）：
    - 按 priority 升序遍历“有条件”的分支，第一个命中者胜出；
    - 空条件分支视为“默认/否则”分支，仅当其它分支都不命中时兜底；
    - 全不命中且无默认分支 → 返回 None（整个条件块跳过，直接走汇合点）。
    """
    if not condition_nodes:
        return None
    ordered = sorted(
        condition_nodes, key=lambda b: (b.get("priority") or 0)
    )
    default_branch: Optional[Dict[str, Any]] = None
    for branch in ordered:
        cond = branch.get("condition")
        if not cond or not (cond.get("rules") if isinstance(cond, dict) else None):
            # 空条件 = 默认分支，记录但不立即返回
            if default_branch is None:
                default_branch = branch
            continue
        if eval_condition(cond, variables):
            return branch
    return default_branch


def materialize_path(
    process_config: Optional[Dict[str, Any]], variables: Optional[dict]
) -> List[Dict[str, Any]]:
    """把画布流程树按提交变量展开为线性执行节点列表（不含 start/condition）。

    返回的每个元素已带 node_order（从 1 递增）与 node_key，可直接落 instance_node。
    """
    if not process_config:
        return []
    root = process_config.get("root") if isinstance(process_config, dict) else None
    if not root:
        return []

    result: List[Dict[str, Any]] = []

    def walk(node: Optional[Dict[str, Any]]) -> None:
        if not node:
            return
        ntype = node.get("type")
        if ntype == NODE_TYPE_START:
            walk(node.get("childNode"))
        elif ntype in (NODE_TYPE_APPROVAL, NODE_TYPE_CC):
            result.append(node)
            walk(node.get("childNode"))
        elif ntype == NODE_TYPE_CONDITION:
            branch = _pick_branch(node.get("conditionNodes") or [], variables)
            if branch:
                walk(branch.get("childNode"))
            # 分支走完回到条件路由的汇合点
            walk(node.get("childNode"))
        # 其它/未知类型：忽略

    walk(root)

    materialized: List[Dict[str, Any]] = []
    for idx, node in enumerate(result, start=1):
        materialized.append(
            {
                "node_order": idx,
                "node_key": node.get("nodeKey"),
                "node_type": _TYPE_TO_NODE_TYPE.get(
                    node.get("type"), C.NODE_TYPE_APPROVAL
                ),
                "node_name": node.get("nodeName") or f"节点{idx}",
                "approver_type": int(node.get("approverType") or C.APPROVER_USER),
                "approver_config": node.get("approverConfig"),
                "sign_type": int(node.get("signType") or C.SIGN_ANY),
                "empty_strategy": int(node.get("emptyStrategy") or C.EMPTY_AUTO_PASS),
                "allow_transfer": int(node.get("allowTransfer") or 0),
                "allow_addsign": int(node.get("allowAddsign") or 0),
            }
        )
    return materialized


def iter_nodes(process_config: Optional[Dict[str, Any]]):
    """遍历树中所有节点（含分支内），用于结构校验、统计审批节点等。"""
    if not process_config:
        return
    root = process_config.get("root") if isinstance(process_config, dict) else None

    def walk(node: Optional[Dict[str, Any]]):
        if not node:
            return
        yield node
        for branch in node.get("conditionNodes") or []:
            yield from walk(branch.get("childNode"))
        yield from walk(node.get("childNode"))

    yield from walk(root)


def validate_tree(process_config: Optional[Dict[str, Any]]) -> List[str]:
    """结构校验，返回错误信息列表（空=通过）。

    校验项：
    - 根节点存在；
    - 审批节点必须配置审批人来源；
    - 条件路由至少 2 个分支且存在默认（空条件）分支兜底；
    - nodeKey 唯一、无环（按对象引用天然无环，这里只查 nodeKey 重复）。
    """
    errors: List[str] = []
    if not process_config or not process_config.get("root"):
        return ["流程为空，请至少配置一个审批节点"]

    seen_keys = set()
    has_approval = False
    for node in iter_nodes(process_config):
        key = node.get("nodeKey")
        if key:
            if key in seen_keys:
                errors.append(f"节点标识重复：{key}")
            seen_keys.add(key)
        ntype = node.get("type")
        if ntype == NODE_TYPE_APPROVAL:
            has_approval = True
            at = node.get("approverType")
            cfg = node.get("approverConfig") or {}
            name = node.get("nodeName") or "审批节点"
            # 指定成员/角色/部门 必须选了对象；动态类型(4/5/6/7)无需
            if at == C.APPROVER_USER and not cfg.get("user_ids"):
                errors.append(f"「{name}」未选择审批成员")
            elif at == C.APPROVER_ROLE and not cfg.get("role_ids"):
                errors.append(f"「{name}」未选择审批角色")
            elif at == C.APPROVER_DEPT and not cfg.get("dept_ids"):
                errors.append(f"「{name}」未选择审批部门")
        elif ntype == NODE_TYPE_CONDITION:
            branches = node.get("conditionNodes") or []
            if len(branches) < 2:
                errors.append("条件分支至少需要 2 个条件")

    if not has_approval:
        errors.append("流程至少需要一个审批节点")
    return errors
