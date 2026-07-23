"""任务级费用单「发起节点」规则 · 纯逻辑（零 DB）测试

覆盖 ``finance_stage_rules`` 的解析 / 判定 / 校验三段核心逻辑：
  - ``default_rules`` / ``default_stage_rules_json``：默认「全类型全节点放开、不拦截」
  - ``parse_stage_rules``：默认 / 缺失 / 空串 / 非法 JSON / 顶层非对象 / 部分类型缺失
    / 非法 key / statuses 非数组 / 空集合 / 超出 DocType 的 key
  - ``creatable_doc_types``：给定任务节点返回可发起单据类型（按 DocType.ALL 顺序）
  - ``assert_stage_allowed``：enforce=True 不允许抛 BizException、允许放行；
    enforce=False 不允许仅软提示放行；doc_type 缺失默认放行

对应需求：任务级费用单·发起节点配置（biz_system_config → finance.task_doc_stage_rules）
对应代码：backend/app/modules/client/services/finance/base/finance_stage_rules.py
覆盖用例：TC-CLI-FINSTAGE-001 ~ TC-CLI-FINSTAGE-018
"""

from __future__ import annotations

import json

import pytest

from app.common.exceptions import BizException
from app.modules.client.services.finance.base.constants import DocType
from app.modules.client.services.finance.base.finance_stage_rules import (
    ALL_TASK_STATUSES,
    DOC_TYPE_LABELS,
    STAGE_RULES_CONFIG_GROUP,
    STAGE_RULES_CONFIG_KEY,
    assert_stage_allowed,
    creatable_doc_types,
    default_rules,
    default_stage_rules_json,
    parse_stage_rules,
)

# 全部任务节点集合（-1 待分配 … 9 已取消）
_ALL = set(ALL_TASK_STATUSES)


# =====================================================================
# 默认规则 / 默认 JSON
# =====================================================================
class TestDefaults:
    def test_default_rules_cover_all_types_and_statuses(self):
        """TC-CLI-FINSTAGE-001 默认规则覆盖全部单据类型 × 全部节点。"""
        rules = default_rules()
        assert set(rules.keys()) == set(DocType.ALL)
        for dt in DocType.ALL:
            assert set(rules[dt]) == _ALL

    def test_default_json_parses_to_open_and_not_enforced(self):
        """TC-CLI-FINSTAGE-002 默认 JSON 可解析、enforce=false、全放开。"""
        raw = default_stage_rules_json()
        obj = json.loads(raw)  # 必须是合法 JSON
        assert obj["enforce"] is False
        # rules 的 key 为字符串化 docType，value 为全节点
        assert set(obj["rules"].keys()) == {str(dt) for dt in DocType.ALL}

        enforce, rules = parse_stage_rules(raw)
        assert enforce is False
        for dt in DocType.ALL:
            assert rules[dt] == _ALL

    def test_config_constants(self):
        """TC-CLI-FINSTAGE-018 常量：配置键/分组 + 单据中文名 + 全节点集合。"""
        assert STAGE_RULES_CONFIG_KEY == "finance.task_doc_stage_rules"
        assert STAGE_RULES_CONFIG_GROUP == "finance"
        assert set(DOC_TYPE_LABELS.keys()) == set(DocType.ALL)
        # 全部节点应含 -1（待分配）与 9（已取消）等边界
        assert -1 in _ALL and 0 in _ALL and 9 in _ALL


# =====================================================================
# parse_stage_rules 回退与解析
# =====================================================================
class TestParseStageRules:
    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_missing_or_blank_falls_back_to_open(self, value):
        """TC-CLI-FINSTAGE-003/004 配置缺失/空串 → (False, 全放开)。"""
        enforce, rules = parse_stage_rules(value)
        assert enforce is False
        for dt in DocType.ALL:
            assert rules[dt] == _ALL

    def test_invalid_json_falls_back_to_open(self):
        """TC-CLI-FINSTAGE-005 非法 JSON → 回退默认全放开、不拦截。"""
        enforce, rules = parse_stage_rules("{not a valid json")
        assert enforce is False
        for dt in DocType.ALL:
            assert rules[dt] == _ALL

    def test_non_object_top_level_falls_back(self):
        """TC-CLI-FINSTAGE-006 顶层为数组（非对象）→ 回退默认。"""
        enforce, rules = parse_stage_rules("[1, 2, 3]")
        assert enforce is False
        for dt in DocType.ALL:
            assert rules[dt] == _ALL

    def test_enforce_true_with_partial_rules(self):
        """TC-CLI-FINSTAGE-007 enforce=true + 部分类型：指定生效，缺失类型全放开。"""
        raw = json.dumps({
            "enforce": True,
            "rules": {
                str(DocType.PREPAY): [-1, 0, 1],
                str(DocType.SETTLE): [5],
            },
        })
        enforce, rules = parse_stage_rules(raw)
        assert enforce is True
        assert rules[DocType.PREPAY] == {-1, 0, 1}
        assert rules[DocType.SETTLE] == {5}
        # 未配置的补款单 / 承包单 → 保持默认全放开
        assert rules[DocType.SUPPLEMENT] == _ALL
        assert rules[DocType.CONTRACTED] == _ALL

    def test_non_int_key_and_non_list_statuses_ignored(self):
        """TC-CLI-FINSTAGE-008 非数字 key 忽略；statuses 非数组忽略（保留默认）。"""
        raw = json.dumps({
            "enforce": True,
            "rules": {
                "abc": [1, 2],                 # 非数字 key → 跳过
                str(DocType.SUPPLEMENT): "5",  # value 非 list → 保留默认全放开
            },
        })
        enforce, rules = parse_stage_rules(raw)
        assert enforce is True
        # 补款单 value 非法 → 未被覆盖，仍为默认全放开
        assert rules[DocType.SUPPLEMENT] == _ALL

    def test_empty_status_list_means_no_creatable_stage(self):
        """TC-CLI-FINSTAGE-009 空节点列表 → 该类型任何节点都不可发起。"""
        raw = json.dumps({
            "enforce": True,
            "rules": {str(DocType.CONTRACTED): []},
        })
        _, rules = parse_stage_rules(raw)
        assert rules[DocType.CONTRACTED] == set()

    def test_unknown_doc_type_key_ignored(self):
        """TC-CLI-FINSTAGE-010 超出 DocType.ALL 的 key（如 99）被忽略。"""
        raw = json.dumps({
            "enforce": False,
            "rules": {"99": [1, 2, 3]},
        })
        enforce, rules = parse_stage_rules(raw)
        assert 99 not in rules
        assert set(rules.keys()) == set(DocType.ALL)


# =====================================================================
# creatable_doc_types
# =====================================================================
class TestCreatableDocTypes:
    def test_pending_assign_stage(self):
        """TC-CLI-FINSTAGE-011 待分配(-1)节点：仅返回配置允许的类型，按 ALL 顺序。"""
        rules = {
            DocType.PREPAY: {-1, 0},
            DocType.SUPPLEMENT: {5},
            DocType.SETTLE: {5},
            DocType.CONTRACTED: {-1},
        }
        assert creatable_doc_types(-1, rules) == [DocType.PREPAY, DocType.CONTRACTED]

    @pytest.mark.parametrize("status,expected", [
        (0, [DocType.PREPAY]),                         # 待派车仅预付
        (5, [DocType.SUPPLEMENT, DocType.SETTLE]),     # 已签收：补款+结算
        (3, []),                                       # 在途：无
    ])
    def test_various_stages(self, status, expected):
        """TC-CLI-FINSTAGE-012 各节点结果（参数化）。"""
        rules = {
            DocType.PREPAY: {-1, 0, 1},
            DocType.SUPPLEMENT: {5},
            DocType.SETTLE: {5, 7},
            DocType.CONTRACTED: {-1},
        }
        assert creatable_doc_types(status, rules) == expected

    def test_default_rules_allow_all_types(self):
        """默认全放开时任意节点都可发起全部类型。"""
        _, rules = parse_stage_rules(None)
        assert creatable_doc_types(3, rules) == list(DocType.ALL)


# =====================================================================
# assert_stage_allowed
# =====================================================================
class TestAssertStageAllowed:
    def test_enforce_true_not_allowed_raises(self):
        """TC-CLI-FINSTAGE-013 enforce=true 且不允许 → 抛 BizException。"""
        rules = {DocType.PREPAY: {-1, 0}}
        with pytest.raises(BizException):
            assert_stage_allowed(DocType.PREPAY, task_status=3,
                                 enforce=True, rules=rules)

    def test_enforce_true_allowed_passes(self):
        """TC-CLI-FINSTAGE-014 enforce=true 且允许 → 放行（无异常）。"""
        rules = {DocType.PREPAY: {-1, 0, 3}}
        assert_stage_allowed(DocType.PREPAY, task_status=3,
                             enforce=True, rules=rules)  # 不抛即通过

    def test_enforce_false_not_allowed_soft_passes(self):
        """TC-CLI-FINSTAGE-015 enforce=false 且不允许 → 仅软提示，放行不拦截。"""
        rules = {DocType.PREPAY: {-1, 0}}
        # 软提示模式：不抛异常
        assert_stage_allowed(DocType.PREPAY, task_status=3,
                             enforce=False, rules=rules)

    def test_missing_doc_type_defaults_allowed(self):
        """TC-CLI-FINSTAGE-016 rules 缺失该 docType → 默认放行（向后兼容）。"""
        # 即便 enforce=true，缺失键回退「全节点允许」
        assert_stage_allowed(DocType.SETTLE, task_status=3,
                             enforce=True, rules={})

    def test_block_message_is_humanized(self):
        """TC-CLI-FINSTAGE-017 拦截文案含节点与单据中文名，且不含技术词。"""
        rules = {DocType.SETTLE: {5}}
        with pytest.raises(BizException) as ei:
            assert_stage_allowed(DocType.SETTLE, task_status=0,
                                 enforce=True, rules=rules)
        msg = str(ei.value)
        assert "结算单" in msg
        assert "待派车" in msg
        # 不应泄露技术字段/编码
        for tech in ("status", "docType", "doc_type", "500", "None"):
            assert tech not in msg
