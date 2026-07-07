"""运营调度与运单 · 状态机联动（纯逻辑，零 DB）测试

聚焦企业端「运单 ↔ 任务单」调度关心的关键不变量（与根目录
tests/test_state_machines.py 的穷举矩阵互补，此处偏业务语义断言）：
  - Task 正向/反向/取消/强制取消门槛
  - Item 由 Task 状态派生（聚合）
  - Waybill 删除/新增挂接门槛、终态

对应需求：项目文档/02.需求文档/02.企业端/06.运营调度模块/
          02.运单与任务单状态机联动设计.md
对应代码：backend/app/modules/client/services/state_machine/**
覆盖用例：TC-CLI-TASK-001 ~ TC-CLI-TASK-015、TC-CLI-WAYBILL-001 ~ 010
"""

from __future__ import annotations

import pytest

from app.common.exceptions import BizException
from app.modules.client.services.state_machine.item_state_machine import (
    ITEM_UNFINISHED_THRESHOLD,
    ItemStateMachine,
)
from app.modules.client.services.state_machine.task_state_machine import (
    TaskStateMachine,
)
from app.modules.client.services.state_machine.waybill_state_machine import (
    WaybillStateMachine,
)


class TestTaskBusinessInvariants:
    def test_signed_can_only_close(self):
        assert TaskStateMachine.legal_next(5) == {7}

    def test_aggregated_states_no_manual_forward(self):
        # 运输中/部分签收/待签收为聚合派生态，不允许人工正向推进
        assert TaskStateMachine.legal_next(3) == set()
        assert TaskStateMachine.legal_next(4) == set()

    def test_terminal_no_next(self):
        assert TaskStateMachine.legal_next(7) == set()
        assert TaskStateMachine.legal_next(9) == set()

    def test_revert_is_single_step(self):
        assert TaskStateMachine.legal_revert(2) == {1}

    def test_illegal_forward_raises(self):
        with pytest.raises(BizException):
            TaskStateMachine.assert_transition(0, 5)


class TestItemDerivation:
    @pytest.mark.parametrize("task_status,expected", [
        (-1, 0), (0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 3), (7, 3), (9, 9),
    ])
    def test_derive_from_task(self, task_status, expected):
        assert ItemStateMachine.derive_from_task(task_status) == expected

    def test_unknown_task_status_none(self):
        assert ItemStateMachine.derive_from_task(123) is None

    def test_unfinished_threshold_semantics(self):
        assert ITEM_UNFINISHED_THRESHOLD == 3
        assert ItemStateMachine.is_unfinished(2) is True
        assert ItemStateMachine.is_unfinished(3) is False


class TestWaybillGuards:
    def test_delete_blocked_by_active_items(self):
        assert WaybillStateMachine.allows_delete(1, has_active_task_items=True) is False

    def test_delete_allowed_when_idle(self):
        assert WaybillStateMachine.allows_delete(0, has_active_task_items=False) is True

    def test_terminal_state(self):
        assert WaybillStateMachine.is_terminal(7) is True

    def test_sign_unsign_paths(self):
        WaybillStateMachine.assert_transition(5, 4)   # 撤销签收
        WaybillStateMachine.assert_transition(5, 6)   # 回单
        WaybillStateMachine.assert_transition(6, 5)   # 撤销回单
