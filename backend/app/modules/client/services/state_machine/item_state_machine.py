"""任务挂接货物（TaskWaybillItem）状态机

Item.status 状态空间：
    0 待装车（默认，挂接后即此态）
    1 已装车（由装车记录 ``TaskLoadingRecord(event_type=1)`` 驱动写入）
    2 已卸车（由卸车记录 ``TaskLoadingRecord(event_type=2)`` 驱动写入）
    3 已交车（客户逐台验车交接完成）
    9 已取消（挂接被取消、任务被取消则同步设为此态）

Item 状态主要由"装卸记录 / 交车事件"驱动，``derive_from_task`` 仅在
非装卸跳转（如出发 / 取消 / 关闭）时为兜底用途。
"""

from typing import Optional, Set

from app.common.exceptions import BizException


ITEM_PENDING = 0
ITEM_LOADED = 1
ITEM_UNLOADED = 2
ITEM_SIGNED = 3
ITEM_CANCELLED = 9

# 兼容历史命名（早期把 status=2 标注为「在途/到达」，现已重定义为「已卸车」）
ITEM_IN_TRANSIT = ITEM_UNLOADED


ITEM_STATUS_LABELS: dict[int, str] = {
    0: "待装车",
    1: "已装车",
    2: "已卸车",
    3: "已交车",
    9: "已取消",
}


# 正向 / 反向合一的合法跳转
ITEM_VALID_TRANS: dict[int, Set[int]] = {
    0: {1, 9},
    1: {0, 2, 9},      # 1→0 撤销装车（撤回最后一条装车记录）
    2: {1, 3, 9},      # 2→1 撤销卸车（撤回最后一条卸车记录）
    3: {2, 9},         # 3→2 撤销交车
    9: set(),
}


# Task.status → Item 目标状态 的"等价表"
# 用法：装卸事件不走此表（由 LoadingRecord 直接驱动 item 状态）；
# 此表仅在非装卸跳转中作为 propagate 的兜底（出发 / 关闭 / 取消等场景）。
# 注意：
#   - task=2 / 4 / 5 由 item 聚合驱动写入，propagate 时 derive 出来的目标
#     与现状一致，目标 ≤ 当前 → propagate 跳过，不会越权写 item；
#   - task=3 在途时 item 仍保持「已装车=1」，避免错误跨步推 item 至 2 已卸车。
_TASK_TO_ITEM: dict[int, int] = {
    -1: 0,
    0: 0,
    1: 0,
    2: 1,
    3: 1,
    4: 2,
    5: 3,
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
