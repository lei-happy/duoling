"""任务挂接货物（TaskWaybillItem）状态机

Item.status 状态空间：
    0 待装车（默认，挂接后即此态）
    1 已装车
    2 在途/已到达（合并语义，由 Task 段状态/任务态决定）
    3 已签收
    9 已取消（挂接被取消、任务被取消则同步设为此态）

Item 状态由 Task 状态变更同步推导，service 层只调用 `derive_from_task`
来得到目标态，再用 `assert_transition` 做合法性校验。
"""

from typing import Optional, Set

from app.common.exceptions import BizException


ITEM_PENDING = 0
ITEM_LOADED = 1
ITEM_IN_TRANSIT = 2
ITEM_SIGNED = 3
ITEM_CANCELLED = 9


ITEM_STATUS_LABELS: dict[int, str] = {
    0: "待装车",
    1: "已装车",
    2: "在途/到达",
    3: "已签收",
    9: "已取消",
}


# 正向 / 反向合一的合法跳转
ITEM_VALID_TRANS: dict[int, Set[int]] = {
    0: {1, 9},
    1: {0, 2, 9},      # 1→0 撤销装车
    2: {1, 3, 9},      # 2→1 撤回出发/到达
    3: {2, 9},         # 3→2 撤销签收
    9: set(),
}


# Task.status → Item 目标状态 的"等价表"
# 用于 Task 推动 Item 正向/反向同步
_TASK_TO_ITEM: dict[int, int] = {
    -1: 0,
    0: 0,
    1: 0,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 3,
    9: 9,
}


# Item 状态作为"已完成"门槛的阈值（聚合用）
ITEM_FINAL_STATES: Set[int] = {3, 9}


# Item "未完成"阈值（用于 cargo.allocated_quantity 释放判断）
# 与现有 task_waybill_item_service.UNFINISHED_THRESHOLD = 3 保持一致
ITEM_UNFINISHED_THRESHOLD: int = 3


def label(status: int) -> str:
    return ITEM_STATUS_LABELS.get(status, str(status))


class ItemStateMachine:
    """挂接货物状态机工具方法"""

    @staticmethod
    def assert_transition(old: int, new: int) -> None:
        if old == new:
            return
        valid = ITEM_VALID_TRANS.get(old, set())
        if new not in valid:
            raise BizException(
                f"挂接货物状态从「{label(old)}」"
                f"不能跳转到「{label(new)}」"
            )

    @staticmethod
    def derive_from_task(task_status: int) -> Optional[int]:
        """根据任务单状态推导挂接货物的目标状态。

        无映射时返回 None（调用方应保留原状态）。
        """
        return _TASK_TO_ITEM.get(task_status)

    @staticmethod
    def is_final(status: int) -> bool:
        return status in ITEM_FINAL_STATES

    @staticmethod
    def is_unfinished(status: int) -> bool:
        return status < ITEM_UNFINISHED_THRESHOLD
