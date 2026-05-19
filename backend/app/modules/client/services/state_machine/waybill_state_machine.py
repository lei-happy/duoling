"""运单状态机

Waybill.status 状态空间（重新语义化后）：
    0 草稿（不再使用，保留兼容）
    1 待调度（可挂接，可编辑/删除）
    2 调度中（部分或全部货物已挂接到任务单，但未全部装车）
    3 运输中（任意货物进入装车/在途）
    4 已送达（聚合门槛：全量货物到达）
    5 已完成（聚合门槛：全量货物签收）
    6 已关闭（终态，可在任意非草稿状态进入）

Waybill 状态由聚合器 `WaybillStatusAggregator` 推导，不应由用户直接传值；
仍保留 `update_status` API 用于运营兜底（例如手动关闭），但需经状态机校验。
"""

from typing import Set

from app.common.exceptions import BizException


WAYBILL_DRAFT = 0
WAYBILL_PENDING = 1
WAYBILL_SCHEDULING = 2
WAYBILL_IN_TRANSIT = 3
WAYBILL_DELIVERED = 4
WAYBILL_COMPLETED = 5
WAYBILL_CLOSED = 6


WAYBILL_STATUS_LABELS: dict[int, str] = {
    0: "草稿",
    1: "待调度",
    2: "调度中",
    3: "运输中",
    4: "已送达",
    5: "已完成",
    6: "已关闭",
}


# 正向 + 反向合一的合法跳转（聚合器内部会按需正/反向推进）
WAYBILL_VALID_TRANS: dict[int, Set[int]] = {
    0: {1, 6},
    1: {2, 6},
    2: {1, 3, 6},        # 调度中可回退到待调度（全部任务取消挂接）
    3: {2, 4, 6},        # 运输中可回退到调度中（所有任务回退到挂接但未装车）
    4: {3, 5, 6},        # 已送达可回退到运输中（撤销到达）
    5: {4, 6},           # 已完成可回退到已送达（撤销签收）
    6: set(),            # 已关闭终态
}


# 已挂接活跃任务时，不允许的用户操作目标
# （删除运单、回到草稿/待调度等）
WAYBILL_STATES_BLOCKING_DELETE: Set[int] = {2, 3, 4, 5}


# 禁止新挂接的运单态（>=4 已送达起，不再允许新任务挂接）
WAYBILL_STATES_BLOCKING_NEW_ITEM: Set[int] = {4, 5, 6}


def label(status: int) -> str:
    return WAYBILL_STATUS_LABELS.get(status, str(status))


class WaybillStateMachine:
    """运单状态机工具方法"""

    @staticmethod
    def assert_transition(old: int, new: int) -> None:
        """统一跳转校验。正/反向都用同一张表，由聚合器保证语义。"""
        if old == new:
            return
        valid = WAYBILL_VALID_TRANS.get(old, set())
        if new not in valid:
            raise BizException(
                f"运单状态从「{label(old)}」"
                f"不能跳转到「{label(new)}」"
            )

    @staticmethod
    def allows_new_item(status: int) -> bool:
        """运单是否允许新增任务挂接（waybillItems）"""
        return status not in WAYBILL_STATES_BLOCKING_NEW_ITEM

    @staticmethod
    def allows_delete(status: int, has_active_task_items: bool) -> bool:
        """运单是否允许删除/编辑核心字段：状态 ≤ 待调度 且 无活跃挂接"""
        if status in WAYBILL_STATES_BLOCKING_DELETE:
            return False
        if has_active_task_items:
            return False
        return True

    @staticmethod
    def is_terminal(status: int) -> bool:
        return status == WAYBILL_CLOSED
