"""服务平台 · 挂牌状态机测试

状态会被四类角色改动（发布方、运营、成交流程、巡检 Worker），流转表是它们
共用的唯一判据。这里把表本身钉死，尤其是两处容易被「顺手放开」的约束：

1. 已下架只能回到待审核，不能直接回展示中——否则下架再上架就绕过了运营处置。
2. 已锁定与履约中不能下架——那会留下指向已下架挂牌的孤儿成交单。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/01.架构与撮合内核设计.md §4.2
对应代码：backend/app/modules/client/services/ecosystem/post_state_machine.py
"""

from __future__ import annotations

import pytest

from app.common.exceptions import BizException
from app.modules.client.services.ecosystem.post_state_machine import (
    ALLOWED_TRANSITIONS,
    STATUS_LABELS,
    assert_transit,
    can_transit,
    describe,
    is_editable,
    is_terminal,
)
from app.modules.console.models.ecosystem.constants import PostStatus

ALL_STATUSES = (
    PostStatus.DRAFT,
    PostStatus.AUDITING,
    PostStatus.REJECTED,
    PostStatus.LISTED,
    PostStatus.LOCKED,
    PostStatus.FULFILLING,
    PostStatus.FINISHED,
    PostStatus.DELISTED,
    PostStatus.CANCELLED,
)


class TestTable:
    def test_every_status_is_in_the_table(self):
        """漏一个状态，那个状态下的所有流转都会被判非法而卡死"""
        assert set(ALLOWED_TRANSITIONS) == set(ALL_STATUSES)

    def test_every_status_has_a_label(self):
        """没有中文名的状态会让用户看到「未知状态」"""
        assert set(STATUS_LABELS) == set(ALL_STATUSES)

    def test_targets_are_all_known_statuses(self):
        for froms, tos in ALLOWED_TRANSITIONS.items():
            for to in tos:
                assert to in ALL_STATUSES, f"{froms} → {to} 指向了表外状态"


class TestHappyPath:
    @pytest.mark.parametrize(
        "src,dst",
        [
            (PostStatus.DRAFT, PostStatus.AUDITING),
            (PostStatus.AUDITING, PostStatus.LISTED),
            (PostStatus.AUDITING, PostStatus.REJECTED),
            (PostStatus.REJECTED, PostStatus.AUDITING),
            (PostStatus.LISTED, PostStatus.LOCKED),
            (PostStatus.LOCKED, PostStatus.FULFILLING),
            (PostStatus.LOCKED, PostStatus.LISTED),
            (PostStatus.FULFILLING, PostStatus.FINISHED),
            (PostStatus.FULFILLING, PostStatus.CANCELLED),
        ],
    )
    def test_documented_transitions_are_allowed(self, src, dst):
        assert can_transit(src, dst)

    def test_listed_can_go_back_to_auditing_for_full_reaudit(self):
        """编辑了核心信息要回待审核，这条状态图上没画但规则要求（04 §2.4）"""
        assert can_transit(PostStatus.LISTED, PostStatus.AUDITING)

    def test_same_status_is_allowed(self):
        """快速复审保持原状态，复用同一个判定函数，原地不动必须合法"""
        for s in ALL_STATUSES:
            assert can_transit(s, s)


class TestDelistPaths:
    @pytest.mark.parametrize(
        "src",
        [PostStatus.DRAFT, PostStatus.AUDITING, PostStatus.REJECTED, PostStatus.LISTED],
    )
    def test_can_delist_before_any_deal_exists(self, src):
        """待审核也要能下架：源单联动可能在挂牌还排队时就判定信息失效"""
        assert can_transit(src, PostStatus.DELISTED)

    @pytest.mark.parametrize("src", [PostStatus.LOCKED, PostStatus.FULFILLING])
    def test_cannot_delist_while_a_deal_is_running(self, src):
        """从挂牌侧抽走会留下孤儿成交单，这类违规要走成交单终止流程"""
        assert not can_transit(src, PostStatus.DELISTED)


class TestRelistMustBeReaudited:
    def test_delisted_goes_to_auditing(self):
        assert can_transit(PostStatus.DELISTED, PostStatus.AUDITING)

    def test_delisted_cannot_jump_straight_back_to_hall(self):
        """这是防「下架再上架绕过处置」的关键一条"""
        assert not can_transit(PostStatus.DELISTED, PostStatus.LISTED)

    def test_delisted_has_exactly_one_way_out(self):
        assert ALLOWED_TRANSITIONS[PostStatus.DELISTED] == frozenset(
            {PostStatus.AUDITING}
        )


class TestTerminalStatuses:
    @pytest.mark.parametrize("src", [PostStatus.FINISHED, PostStatus.CANCELLED])
    def test_no_way_out(self, src):
        assert ALLOWED_TRANSITIONS[src] == frozenset()

    def test_is_terminal_matches_constants(self):
        for s in ALL_STATUSES:
            assert is_terminal(s) == (s in PostStatus.TERMINAL)

    def test_is_terminal_tolerates_none(self):
        assert is_terminal(None) is False


class TestEditable:
    @pytest.mark.parametrize(
        "src",
        [
            PostStatus.DRAFT,
            PostStatus.REJECTED,
            PostStatus.LISTED,
            PostStatus.DELISTED,
        ],
    )
    def test_editable(self, src):
        assert is_editable(src)

    @pytest.mark.parametrize(
        "src",
        [
            PostStatus.AUDITING,
            PostStatus.LOCKED,
            PostStatus.FULFILLING,
            PostStatus.FINISHED,
            PostStatus.CANCELLED,
        ],
    )
    def test_not_editable(self, src):
        assert not is_editable(src)

    def test_delisted_is_editable_so_the_fix_then_relist_path_works(self):
        """下架后改内容再上架是主要用法，不可编辑会把这条路堵死"""
        assert is_editable(PostStatus.DELISTED)
        assert can_transit(PostStatus.DELISTED, PostStatus.AUDITING)


class TestAssertTransit:
    def test_passes_silently_when_legal(self):
        assert_transit(PostStatus.LISTED, PostStatus.DELISTED, action="停止展示")

    def test_message_names_the_current_status_in_chinese(self):
        with pytest.raises(BizException) as e:
            assert_transit(PostStatus.LOCKED, PostStatus.DELISTED, action="停止展示")
        assert "已锁定" in e.value.message
        assert "停止展示" in e.value.message

    def test_message_carries_the_advice(self):
        with pytest.raises(BizException) as e:
            assert_transit(
                PostStatus.FULFILLING,
                PostStatus.DELISTED,
                action="停止展示",
                advice="需要终止请在「我的合作」里处理",
            )
        assert "我的合作" in e.value.message

    def test_message_has_no_trailing_comma_without_advice(self):
        with pytest.raises(BizException) as e:
            assert_transit(PostStatus.FINISHED, PostStatus.AUDITING, action="重新上架")
        assert not e.value.message.endswith("，")

    def test_message_never_leaks_status_codes(self):
        """用户看到的必须是「已锁定」，不是 status=4"""
        with pytest.raises(BizException) as e:
            assert_transit(PostStatus.LOCKED, PostStatus.DELISTED, action="停止展示")
        assert "status" not in e.value.message.lower()
        assert "4" not in e.value.message


class TestDescribe:
    def test_known(self):
        assert describe(PostStatus.LISTED) == "展示中"

    def test_none(self):
        assert describe(None) == "未知状态"

    def test_unknown_value_does_not_raise(self):
        """历史数据里出现表外取值时，一句能读懂的话比 500 好"""
        assert describe(99) == "未知状态"


class TestNoneSafety:
    @pytest.mark.parametrize(
        "src,dst",
        [(None, PostStatus.LISTED), (PostStatus.LISTED, None), (None, None)],
    )
    def test_none_is_never_a_legal_transition(self, src, dst):
        assert not can_transit(src, dst)
