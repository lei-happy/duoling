"""审批中心（Approval）纯逻辑单元测试

对应需求：doc/02.需求文档/02.企业端/08.审批中心/**
对应后端：
    backend/app/modules/client/services/approval/condition.py（条件 DSL 求值）
    backend/app/modules/client/services/approval/tree.py（画布树 → 线性路径、结构校验）
    backend/app/modules/client/services/approval/resolver.py（审批人解析，DB 无关分支）
对应用例：TC-CLI-APPROVAL-001、TC-CLI-APPROVAL-010 ~ TC-CLI-APPROVAL-039

说明
----
审批中心此前无任何自动化脚本（见 06.审批中心.md「待补/仅手工」）。本脚本聚焦
**零 DB 依赖的核心引擎逻辑**：条件表达式求值、画布流程树展开为线性执行路径、
条件分支互斥选择、流程结构校验、以及审批人解析中不查库的分支（指定成员/发起人/
发起人自选，去重与排除发起人）。这些是审批链路正确性的地基，可稳定、快速回归。

DB 强相关的链路（发起→待办→审批通过/驳回触发业务回调）仍以集成用例/手工登记，
见 06.审批中心.md 其余用例。
"""

from __future__ import annotations

import pytest

from app.modules.client.services.approval import constants as C
from app.modules.client.services.approval.condition import eval_condition, _cmp
from app.modules.client.services.approval.resolver import ApproverResolver
from app.modules.client.services.approval.tree import (
    _pick_branch,
    iter_nodes,
    materialize_path,
    validate_tree,
)


# =====================================================================
# 1) 条件表达式求值 eval_condition / _cmp（TC-CLI-APPROVAL-010 ~ 019）
# =====================================================================
class TestEvalCondition:
    """条件 DSL 求值：空条件恒真、and/or 逻辑、各比较运算、类型容错。"""

    def test_empty_condition_is_true(self):
        """TC-CLI-APPROVAL-010：空条件 / None / 无 rules → 恒真。"""
        assert eval_condition(None, {"amount": 1}) is True
        assert eval_condition({}, {"amount": 1}) is True
        assert eval_condition({"logic": "and", "rules": []}, {"amount": 1}) is True

    def test_and_logic_all_true(self):
        """TC-CLI-APPROVAL-011：and 逻辑全部命中才通过。"""
        cond = {
            "logic": "and",
            "rules": [
                {"field": "amount", "op": ">=", "value": 10000},
                {"field": "doc_type", "op": "in", "value": [3, 9]},
            ],
        }
        assert eval_condition(cond, {"amount": 12000, "doc_type": 3}) is True
        assert eval_condition(cond, {"amount": 9000, "doc_type": 3}) is False
        assert eval_condition(cond, {"amount": 12000, "doc_type": 1}) is False

    def test_or_logic_any_true(self):
        """TC-CLI-APPROVAL-012：or 逻辑任一命中即通过。"""
        cond = {
            "logic": "or",
            "rules": [
                {"field": "amount", "op": ">=", "value": 10000},
                {"field": "vip", "op": "==", "value": True},
            ],
        }
        assert eval_condition(cond, {"amount": 5000, "vip": True}) is True
        assert eval_condition(cond, {"amount": 20000, "vip": False}) is True
        assert eval_condition(cond, {"amount": 5000, "vip": False}) is False

    def test_default_logic_is_and(self):
        """TC-CLI-APPROVAL-013：未指定 logic 默认按 and 处理。"""
        cond = {
            "rules": [
                {"field": "a", "op": "==", "value": 1},
                {"field": "b", "op": "==", "value": 2},
            ]
        }
        assert eval_condition(cond, {"a": 1, "b": 2}) is True
        assert eval_condition(cond, {"a": 1, "b": 3}) is False

    @pytest.mark.parametrize(
        "op,left,right,expected",
        [
            ("==", 1, 1, True),
            ("==", 1, 2, False),
            ("!=", 1, 2, True),
            ("!=", 2, 2, False),
            ("in", 3, [1, 3, 5], True),
            ("in", 4, [1, 3, 5], False),
            ("not_in", 4, [1, 3, 5], True),
            ("not_in", 3, [1, 3, 5], False),
            (">", 5, 3, True),
            (">", 3, 5, False),
            (">=", 5, 5, True),
            (">=", 4, 5, False),
            ("<", 3, 5, True),
            ("<", 5, 3, False),
            ("<=", 5, 5, True),
            ("<=", 6, 5, False),
        ],
    )
    def test_operators(self, op, left, right, expected):
        """TC-CLI-APPROVAL-014：逐一验证各比较运算符。"""
        assert _cmp(left, op, right) is expected

    def test_numeric_coercion(self):
        """TC-CLI-APPROVAL-015：数值比较对字符串数字做 float 容错。"""
        assert _cmp("10000", ">=", 5000) is True
        assert _cmp("abc", ">=", 5000) is False  # 不可转数字 → False

    def test_in_with_none_value(self):
        """TC-CLI-APPROVAL-016：in / not_in 的 value 为 None 视作空集。"""
        assert _cmp(1, "in", None) is False
        assert _cmp(1, "not_in", None) is True

    def test_unknown_operator_false(self):
        """TC-CLI-APPROVAL-017：未知运算符返回 False（安全兜底）。"""
        assert _cmp(1, "%%", 1) is False

    def test_missing_variable_treated_as_none(self):
        """TC-CLI-APPROVAL-018：变量缺失时取 None 参与比较，不抛异常。"""
        cond = {"rules": [{"field": "amount", "op": ">=", "value": 100}]}
        assert eval_condition(cond, {}) is False
        assert eval_condition(cond, None) is False


# =====================================================================
# 2) 条件分支互斥选择 _pick_branch（TC-CLI-APPROVAL-020 ~ 024）
# =====================================================================
class TestPickBranch:
    """条件路由：按优先级升序取第一个命中分支，空条件为默认兜底。"""

    def _branch(self, key, priority, rules=None):
        cond = {"logic": "and", "rules": rules} if rules is not None else None
        return {"nodeKey": key, "priority": priority, "condition": cond}

    def test_priority_order_first_match_wins(self):
        """TC-CLI-APPROVAL-020：多个命中时，priority 小者优先。"""
        branches = [
            self._branch("b2", 2, [{"field": "amount", "op": ">=", "value": 1000}]),
            self._branch("b1", 1, [{"field": "amount", "op": ">=", "value": 500}]),
        ]
        picked = _pick_branch(branches, {"amount": 2000})
        assert picked["nodeKey"] == "b1"

    def test_default_branch_fallback(self):
        """TC-CLI-APPROVAL-021：条件分支都不命中时走空条件默认分支。"""
        branches = [
            self._branch("cond", 1, [{"field": "amount", "op": ">=", "value": 10000}]),
            self._branch("default", 2, None),
        ]
        picked = _pick_branch(branches, {"amount": 100})
        assert picked["nodeKey"] == "default"

    def test_no_match_no_default_returns_none(self):
        """TC-CLI-APPROVAL-022：全不命中且无默认分支 → None（跳过条件块）。"""
        branches = [
            self._branch("cond", 1, [{"field": "amount", "op": ">=", "value": 10000}]),
        ]
        assert _pick_branch(branches, {"amount": 100}) is None

    def test_condition_match_beats_default(self):
        """TC-CLI-APPROVAL-023：有条件分支命中时优先于默认分支。"""
        branches = [
            self._branch("default", 5, None),
            self._branch("cond", 1, [{"field": "vip", "op": "==", "value": True}]),
        ]
        picked = _pick_branch(branches, {"vip": True})
        assert picked["nodeKey"] == "cond"

    def test_empty_branches_returns_none(self):
        """TC-CLI-APPROVAL-024：无分支 → None。"""
        assert _pick_branch([], {"amount": 1}) is None


# =====================================================================
# 3) 画布树展开 materialize_path（TC-CLI-APPROVAL-025 ~ 031）
# =====================================================================
def _start(child, **kw):
    node = {"nodeKey": "start", "type": "start", "childNode": child}
    node.update(kw)
    return node


def _approval(key, child=None, **kw):
    node = {
        "nodeKey": key,
        "type": "approval",
        "nodeName": key,
        "approverType": C.APPROVER_USER,
        "approverConfig": {"user_ids": [1]},
        "childNode": child,
    }
    node.update(kw)
    return node


def _cc(key, child=None, **kw):
    node = {"nodeKey": key, "type": "cc", "nodeName": key, "childNode": child}
    node.update(kw)
    return node


def _condition(key, condition_nodes, child=None):
    return {
        "nodeKey": key,
        "type": "condition",
        "conditionNodes": condition_nodes,
        "childNode": child,
    }


class TestMaterializePath:
    """画布流程树按提交变量展开为线性执行节点列表。"""

    def test_empty_config(self):
        """TC-CLI-APPROVAL-025：空配置 / 无 root → 空路径。"""
        assert materialize_path(None, {}) == []
        assert materialize_path({}, {}) == []
        assert materialize_path({"root": None}, {}) == []

    def test_linear_two_approvals(self):
        """TC-CLI-APPROVAL-026：start→审批A→审批B 线性展开，node_order 从 1 递增。"""
        tree = {"root": _start(_approval("A", _approval("B")))}
        path = materialize_path(tree, {})
        assert [n["node_key"] for n in path] == ["A", "B"]
        assert [n["node_order"] for n in path] == [1, 2]
        assert path[0]["node_type"] == C.NODE_TYPE_APPROVAL

    def test_start_node_not_emitted(self):
        """TC-CLI-APPROVAL-027：start 节点不产出为执行节点。"""
        tree = {"root": _start(_approval("A"))}
        path = materialize_path(tree, {})
        assert all(n["node_key"] != "start" for n in path)

    def test_cc_node_type_mapping(self):
        """TC-CLI-APPROVAL-028：抄送节点映射为 NODE_TYPE_CC 并计入路径。"""
        tree = {"root": _start(_cc("cc1", _approval("A")))}
        path = materialize_path(tree, {})
        assert path[0]["node_type"] == C.NODE_TYPE_CC
        assert path[1]["node_type"] == C.NODE_TYPE_APPROVAL

    def test_condition_branch_selected_and_rejoin(self):
        """TC-CLI-APPROVAL-029：条件命中走高额分支，之后回到汇合点。"""
        high = _approval("HIGH")
        low = _approval("LOW")
        cond = _condition(
            "c1",
            condition_nodes=[
                {
                    "nodeKey": "hb",
                    "priority": 1,
                    "condition": {
                        "logic": "and",
                        "rules": [{"field": "amount", "op": ">=", "value": 10000}],
                    },
                    "childNode": high,
                },
                {"nodeKey": "lb", "priority": 2, "condition": None, "childNode": low},
            ],
            child=_approval("FINAL"),
        )
        tree = {"root": _start(cond)}
        high_path = [n["node_key"] for n in materialize_path(tree, {"amount": 20000})]
        low_path = [n["node_key"] for n in materialize_path(tree, {"amount": 100})]
        assert high_path == ["HIGH", "FINAL"]
        assert low_path == ["LOW", "FINAL"]

    def test_condition_no_match_skips_to_rejoin(self):
        """TC-CLI-APPROVAL-030：条件全不命中且无默认分支 → 直接走汇合点。"""
        cond = _condition(
            "c1",
            condition_nodes=[
                {
                    "nodeKey": "hb",
                    "priority": 1,
                    "condition": {
                        "logic": "and",
                        "rules": [{"field": "amount", "op": ">=", "value": 10000}],
                    },
                    "childNode": _approval("HIGH"),
                }
            ],
            child=_approval("FINAL"),
        )
        tree = {"root": _start(cond)}
        path = [n["node_key"] for n in materialize_path(tree, {"amount": 100})]
        assert path == ["FINAL"]

    def test_node_defaults_applied(self):
        """TC-CLI-APPROVAL-031：审批节点缺省 sign_type/empty_strategy 使用默认值。"""
        node = {"nodeKey": "A", "type": "approval", "approverType": C.APPROVER_USER}
        tree = {"root": _start(node)}
        path = materialize_path(tree, {})
        assert path[0]["sign_type"] == C.SIGN_ANY
        assert path[0]["empty_strategy"] == C.EMPTY_AUTO_PASS
        assert path[0]["node_name"] == "节点1"


# =====================================================================
# 4) 流程结构校验 validate_tree / iter_nodes（TC-CLI-APPROVAL-001, 032 ~ 037）
# =====================================================================
class TestValidateTree:
    """流程结构校验：返回错误信息列表，空表示通过。"""

    def test_valid_minimal_flow_passes(self):
        """TC-CLI-APPROVAL-001：最小合法流程（start + 审批节点）校验通过。"""
        tree = {"root": _start(_approval("A"))}
        assert validate_tree(tree) == []

    def test_empty_flow_error(self):
        """TC-CLI-APPROVAL-032：空流程返回明确错误。"""
        assert validate_tree(None)
        assert validate_tree({"root": None})

    def test_no_approval_node_error(self):
        """TC-CLI-APPROVAL-033：只有抄送、无审批节点 → 报错。"""
        tree = {"root": _start(_cc("cc1"))}
        errors = validate_tree(tree)
        assert any("至少需要一个审批节点" in e for e in errors)

    def test_approver_user_missing_config_error(self):
        """TC-CLI-APPROVAL-034：指定成员审批但未选人 → 报错。"""
        node = {
            "nodeKey": "A",
            "type": "approval",
            "nodeName": "财务审批",
            "approverType": C.APPROVER_USER,
            "approverConfig": {},
        }
        errors = validate_tree({"root": _start(node)})
        assert any("未选择审批成员" in e for e in errors)

    def test_deprecated_approver_type_error(self):
        """TC-CLI-APPROVAL-035：使用已停用审批人类型（发起人/自选）→ 报错。"""
        node = {
            "nodeKey": "A",
            "type": "approval",
            "nodeName": "自选审批",
            "approverType": C.APPROVER_INITIATOR_PICK,
        }
        errors = validate_tree({"root": _start(node)})
        assert any("已停用的审批人类型" in e for e in errors)

    def test_condition_needs_two_branches(self):
        """TC-CLI-APPROVAL-036：条件路由少于 2 个分支 → 报错。"""
        cond = _condition(
            "c1",
            condition_nodes=[
                {"nodeKey": "b1", "priority": 1, "condition": None, "childNode": _approval("A")}
            ],
        )
        errors = validate_tree({"root": _start(cond)})
        assert any("条件分支至少需要 2 个条件" in e for e in errors)

    def test_duplicate_node_key_error(self):
        """TC-CLI-APPROVAL-037：nodeKey 重复 → 报错。"""
        tree = {"root": _start(_approval("DUP", _approval("DUP")))}
        errors = validate_tree(tree)
        assert any("节点标识重复" in e for e in errors)

    def test_iter_nodes_covers_branches(self):
        """TC-CLI-APPROVAL-038：iter_nodes 遍历含条件分支内部的所有节点。"""
        cond = _condition(
            "c1",
            condition_nodes=[
                {"nodeKey": "b1", "priority": 1, "condition": None, "childNode": _approval("IN_BRANCH")},
                {"nodeKey": "b2", "priority": 2, "condition": None, "childNode": None},
            ],
            child=_approval("AFTER"),
        )
        keys = {n.get("nodeKey") for n in iter_nodes({"root": _start(cond)})}
        assert {"start", "c1", "IN_BRANCH", "AFTER"} <= keys


# =====================================================================
# 5) 审批人解析 ApproverResolver（DB 无关分支，TC-CLI-APPROVAL-039）
# =====================================================================
class TestApproverResolverNoDb:
    """审批人解析中不查库的分支：指定成员 / 发起人 / 发起人自选 + 去重排序。"""

    async def test_resolve_specified_users_dedup(self):
        """TC-CLI-APPROVAL-039a：指定成员去重、过滤非法/非正 id。"""
        result = await ApproverResolver.resolve(
            None,
            approver_type=C.APPROVER_USER,
            approver_config={"user_ids": [3, 3, "5", 0, -1, "x", 7]},
            initiator_id=99,
            initiator_dept_id=None,
            variables=None,
        )
        assert result == [3, 5, 7]

    async def test_resolve_initiator(self):
        """TC-CLI-APPROVAL-039b：发起人本人类型返回发起人 id。"""
        result = await ApproverResolver.resolve(
            None,
            approver_type=C.APPROVER_INITIATOR,
            approver_config=None,
            initiator_id=42,
            initiator_dept_id=None,
            variables=None,
        )
        assert result == [42]

    async def test_resolve_skip_initiator(self):
        """TC-CLI-APPROVAL-039c：skip_initiator 排除发起人自己。"""
        result = await ApproverResolver.resolve(
            None,
            approver_type=C.APPROVER_USER,
            approver_config={"user_ids": [1, 2, 42], "skip_initiator": True},
            initiator_id=42,
            initiator_dept_id=None,
            variables=None,
        )
        assert result == [1, 2]

    async def test_resolve_initiator_pick_from_variables(self):
        """TC-CLI-APPROVAL-039d：发起人自选从提交变量 picked_approvers 取值。"""
        result = await ApproverResolver.resolve(
            None,
            approver_type=C.APPROVER_INITIATOR_PICK,
            approver_config=None,
            initiator_id=1,
            initiator_dept_id=None,
            variables={"picked_approvers": [8, 9, 8]},
        )
        assert result == [8, 9]

    async def test_resolve_unknown_type_empty(self):
        """TC-CLI-APPROVAL-039e：未知审批人类型返回空列表。"""
        result = await ApproverResolver.resolve(
            None,
            approver_type=999,
            approver_config={"user_ids": [1]},
            initiator_id=1,
            initiator_dept_id=None,
            variables=None,
        )
        assert result == []
