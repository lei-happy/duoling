"""三层业务状态机单元测试（零 DB 依赖）

覆盖 Task / Item / Waybill 三套状态机的正向、反向、强制取消、取消、
聚合衍生与各类业务门槛判定，作为状态机回归基线。

对应设计：doc/02.需求文档/02.企业端/06.运营调度模块/
        02.运单与任务单状态机联动设计.md
"""

import pytest

from app.common.exceptions import BizException
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_CANCEL_FROM,
    TASK_FORCE_CANCEL_FROM,
    TASK_REVERSE_TRANS,
    TASK_VALID_TRANS,
    TaskStateMachine,
)
from app.modules.client.services.state_machine.item_state_machine import (
    ITEM_FINAL_STATES,
    ITEM_UNFINISHED_THRESHOLD,
    ITEM_VALID_TRANS,
    ItemStateMachine,
)
from app.modules.client.services.state_machine.waybill_state_machine import (
    WAYBILL_STATES_BLOCKING_DELETE,
    WAYBILL_STATES_BLOCKING_NEW_ITEM,
    WAYBILL_VALID_TRANS,
    WaybillStateMachine,
)


# 三套状态机各自完整的状态空间（用于穷举"非法跳转"矩阵）
TASK_STATES = [-1, 0, 1, 2, 3, 4, 5, 7, 9]
ITEM_STATES = [0, 1, 2, 3, 9]
WAYBILL_STATES = [0, 1, 2, 3, 4, 5, 6, 7]


def _legal_forward_pairs(trans: dict) -> list:
    return [(old, new) for old, news in trans.items() for new in news]


def _illegal_forward_pairs(trans: dict, states: list) -> list:
    """所有「old != new 且不在合法集合」的跳转对（同态由各机自行短路）。"""
    pairs = []
    for old in states:
        legal = trans.get(old, set())
        for new in states:
            if new == old:
                continue
            if new not in legal:
                pairs.append((old, new))
    return pairs


# =====================================================================
# Task 状态机
# =====================================================================
class TestTaskStateMachine:
    @pytest.mark.parametrize("old,new", _legal_forward_pairs(TASK_VALID_TRANS))
    def test_forward_legal(self, old, new):
        # 合法正向跳转不抛异常
        TaskStateMachine.assert_transition(old, new)

    @pytest.mark.parametrize(
        "old,new", _illegal_forward_pairs(TASK_VALID_TRANS, TASK_STATES)
    )
    def test_forward_illegal(self, old, new):
        with pytest.raises(BizException):
            TaskStateMachine.assert_transition(old, new)

    @pytest.mark.parametrize("old,target", _legal_forward_pairs(TASK_REVERSE_TRANS))
    def test_revert_legal(self, old, target):
        TaskStateMachine.assert_revert(old, target)

    def test_revert_table_is_single_step_back(self):
        # 反向表语义：1→0 / 2→1 / 3→2 / 4→3
        assert TaskStateMachine.legal_revert(1) == {0}
        assert TaskStateMachine.legal_revert(2) == {1}
        assert TaskStateMachine.legal_revert(3) == {2}
        assert TaskStateMachine.legal_revert(4) == {3}

    @pytest.mark.parametrize("bad", [(5, 4), (4, 2), (2, 0), (3, 1), (1, 2)])
    def test_revert_illegal(self, bad):
        # 关键：5→4「撤销签收」不走 revert_status（走 item 反向聚合），此处必须拒绝
        old, target = bad
        with pytest.raises(BizException):
            TaskStateMachine.assert_revert(old, target)

    @pytest.mark.parametrize("old", sorted(TASK_FORCE_CANCEL_FROM))
    def test_force_cancel_allowed(self, old):
        TaskStateMachine.assert_force_cancellable(old)
        assert TaskStateMachine.can_force_cancel(old) is True

    @pytest.mark.parametrize(
        "old", [s for s in TASK_STATES if s not in TASK_FORCE_CANCEL_FROM]
    )
    def test_force_cancel_rejected(self, old):
        with pytest.raises(BizException):
            TaskStateMachine.assert_force_cancellable(old)
        assert TaskStateMachine.can_force_cancel(old) is False

    @pytest.mark.parametrize("old", sorted(TASK_CANCEL_FROM))
    def test_cancel_allowed(self, old):
        TaskStateMachine.assert_cancellable(old)

    @pytest.mark.parametrize(
        "old", [s for s in TASK_STATES if s not in TASK_CANCEL_FROM]
    )
    def test_cancel_rejected(self, old):
        with pytest.raises(BizException):
            TaskStateMachine.assert_cancellable(old)

    def test_signed_can_only_close(self):
        # 已签收(5) 正向仅能 → 已关闭(7)；4→5、3→4、1→2 等聚合态不可人工推进
        assert TaskStateMachine.legal_next(5) == {7}
        assert TaskStateMachine.legal_next(4) == set()
        assert TaskStateMachine.legal_next(3) == set()

    def test_terminal_states_have_no_next(self):
        assert TaskStateMachine.legal_next(7) == set()
        assert TaskStateMachine.legal_next(9) == set()


# =====================================================================
# Item 状态机
# =====================================================================
class TestItemStateMachine:
    @pytest.mark.parametrize("old,new", _legal_forward_pairs(ITEM_VALID_TRANS))
    def test_legal(self, old, new):
        ItemStateMachine.assert_transition(old, new)

    @pytest.mark.parametrize(
        "old,new", _illegal_forward_pairs(ITEM_VALID_TRANS, ITEM_STATES)
    )
    def test_illegal(self, old, new):
        with pytest.raises(BizException):
            ItemStateMachine.assert_transition(old, new)

    @pytest.mark.parametrize("s", ITEM_STATES)
    def test_same_state_is_noop(self, s):
        # old == new 直接放过（幂等）
        ItemStateMachine.assert_transition(s, s)

    def test_un_sign_3_to_2_is_legal(self):
        # 撤销签收的 item 级路径：3→2 合法（驱动 task 5→4 反向聚合）
        ItemStateMachine.assert_transition(3, 2)

    @pytest.mark.parametrize(
        "task_status,expected",
        [
            (-1, 0),
            (0, 0),
            (1, 0),
            (2, 1),
            (3, 1),
            (4, 2),
            (5, 3),
            (7, 3),
            (9, 9),
        ],
    )
    def test_derive_from_task(self, task_status, expected):
        assert ItemStateMachine.derive_from_task(task_status) == expected

    def test_derive_from_task_unknown(self):
        assert ItemStateMachine.derive_from_task(123) is None

    @pytest.mark.parametrize("s", sorted(ITEM_FINAL_STATES))
    def test_is_final(self, s):
        assert ItemStateMachine.is_final(s) is True

    @pytest.mark.parametrize("s", [0, 1, 2])
    def test_is_not_final(self, s):
        assert ItemStateMachine.is_final(s) is False

    @pytest.mark.parametrize("s,expected", [(0, True), (1, True), (2, True), (3, False), (9, False)])
    def test_is_unfinished(self, s, expected):
        # 未完成阈值 = 3（已签收/已取消视为已完成，释放 allocated_quantity）
        assert ItemStateMachine.is_unfinished(s) is expected
        assert ITEM_UNFINISHED_THRESHOLD == 3


# =====================================================================
# Waybill 状态机
# =====================================================================
class TestWaybillStateMachine:
    @pytest.mark.parametrize("old,new", _legal_forward_pairs(WAYBILL_VALID_TRANS))
    def test_legal(self, old, new):
        WaybillStateMachine.assert_transition(old, new)

    @pytest.mark.parametrize(
        "old,new", _illegal_forward_pairs(WAYBILL_VALID_TRANS, WAYBILL_STATES)
    )
    def test_illegal(self, old, new):
        with pytest.raises(BizException):
            WaybillStateMachine.assert_transition(old, new)

    @pytest.mark.parametrize("s", WAYBILL_STATES)
    def test_same_state_is_noop(self, s):
        WaybillStateMachine.assert_transition(s, s)

    def test_sign_and_un_sign_paths(self):
        # 5 已签收 ↔ 4 待签收（撤销签收联动）；5→6 已回单（人工）
        WaybillStateMachine.assert_transition(5, 4)
        WaybillStateMachine.assert_transition(5, 6)
        WaybillStateMachine.assert_transition(6, 5)  # 撤销回单

    def test_cross_step_forward_allowed_for_low_states(self):
        # 待调度可由聚合器跨步推进至任意活跃态（多任务并发装车场景）
        WaybillStateMachine.assert_transition(1, 5)
        WaybillStateMachine.assert_transition(2, 5)

    @pytest.mark.parametrize("s", sorted(WAYBILL_STATES_BLOCKING_NEW_ITEM))
    def test_blocks_new_item(self, s):
        assert WaybillStateMachine.allows_new_item(s) is False

    @pytest.mark.parametrize(
        "s", [x for x in WAYBILL_STATES if x not in WAYBILL_STATES_BLOCKING_NEW_ITEM]
    )
    def test_allows_new_item(self, s):
        assert WaybillStateMachine.allows_new_item(s) is True

    @pytest.mark.parametrize("s", sorted(WAYBILL_STATES_BLOCKING_DELETE))
    def test_delete_blocked_by_status(self, s):
        assert WaybillStateMachine.allows_delete(s, has_active_task_items=False) is False

    def test_delete_blocked_by_active_items(self):
        # 状态允许但有活跃挂接 → 仍不允许删除/改核心字段
        assert WaybillStateMachine.allows_delete(1, has_active_task_items=True) is False

    def test_delete_allowed(self):
        assert WaybillStateMachine.allows_delete(0, has_active_task_items=False) is True
        assert WaybillStateMachine.allows_delete(1, has_active_task_items=False) is True

    def test_is_terminal(self):
        assert WaybillStateMachine.is_terminal(7) is True
        for s in [0, 1, 2, 3, 4, 5, 6]:
            assert WaybillStateMachine.is_terminal(s) is False
