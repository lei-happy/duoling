"""任务单状态机

Task.status 状态空间（已与"财务结算"解耦）：
    -1 待分配 → 0 待派车 → 1 已派车 → 2 已装车 → 3 在途 → 4 已到达
    → 5 已签收（聚合态） → 7 已关闭
    9 已取消（终态，可从 -1/0/1/2 进入）

设计要点：
- 5 已签收 = 聚合态：当任务下所有未取消的 TaskWaybillItem.status=3 时，
  由 ``TaskWaybillItemService._aggregate_task_status_from_items`` 自动 4→5；
  不接受外部 ``update_status(4→5)`` 人工跳转。
- 6 已结算 已彻底移除：财务单据（task_finance_doc）的支付/撤销不再驱动 task.status；
  财务侧只维护 ``task.settled_amount / prepaid_amount / supplement_amount`` 等冗余金额字段。
- 7 已关闭 由 ``close`` 动作（人工）从 5 推进。

正反通道分离：
- 正向跳转表 TASK_VALID_TRANS 由 update_status / 业务动作触发
- 反向跳转表 TASK_REVERSE_TRANS 由 revert_status 单独触发
- TASK_FORCE_CANCEL_FROM 列出可走"强制取消"路径的源态
"""

from typing import Set

from app.common.exceptions import BizException


# 状态值常量
TASK_PENDING_ASSIGN = -1
TASK_PENDING_DISPATCH = 0
TASK_DISPATCHED = 1
TASK_LOADED = 2
TASK_ON_WAY = 3
TASK_ARRIVED = 4
TASK_SIGNED = 5
TASK_CLOSED = 7
TASK_CANCELLED = 9


TASK_STATUS_LABELS: dict[int, str] = {
    -1: "待分配",
    0: "待派车",
    1: "已派车",
    2: "已装车",
    3: "在途",
    4: "已到达",
    5: "已签收",
    7: "已关闭",
    9: "已取消",
}


# 正向合法跳转
# - 4→5 由 item 聚合驱动写入，不在此表内对外暴露；外部 update_status 进入 4 后
#   不能再人工推进，必须靠 item 全签收触发聚合
# - 1→2 / 3→4 同样下沉为 *聚合态*：装车记录 / 卸车记录创建后由
#   ``_aggregate_load_status_from_items`` 写入，不接受外部 update_status 推进；
#   防止跳过装卸记录直接置任务为已装车/已到达
TASK_VALID_TRANS: dict[int, Set[int]] = {
    -1: set(),       # 进入待派车/已派车走 complete_carrier_assignment；取消走 cancel_task
    0: {1, 9},       # 待派车 → 已派车 / 已取消
    1: {0, 9},       # 已派车 → 回退待派车（撤回派车）/ 已取消（1→2 走聚合）
    2: {3, 9},       # 已装车 → 在途 / 已取消
    3: set(),        # 在途 → 已到达 仅由装卸记录聚合驱动
    4: set(),        # 已到达 → 已签收 仅由 item 聚合驱动
    5: {7},          # 已签收 → 已关闭
    7: set(),
    9: set(),
}


# 反向跳转（专项撤销）
# - 1→0 「撤回派车」也保留在正向表里，是历史兼容；优先走 revert
# - 5→4 仅通过 item 反向聚合触发（撤销最后一条签收 item），不通过 revert_status
TASK_REVERSE_TRANS: dict[int, Set[int]] = {
    1: {0},   # 撤回派车
    2: {1},   # 撤销装车
    3: {2},   # 撤回出发
    4: {3},   # 撤回到达
}


# 强制取消可入态（线下取消）
TASK_FORCE_CANCEL_FROM: Set[int] = {2, 3, 4}


# 取消任务（cancel_task，常规取消）可入态
TASK_CANCEL_FROM: Set[int] = {-1, 0, 1, 2}


def label(status: int) -> str:
    return TASK_STATUS_LABELS.get(status, str(status))


class TaskStateMachine:
    """任务单状态机工具方法"""

    @staticmethod
    def assert_transition(old: int, new: int) -> None:
        """正向跳转校验。非法跳转抛 BizException。"""
        valid = TASK_VALID_TRANS.get(old, set())
        if new not in valid:
            raise BizException(
                f"任务单状态从「{label(old)}」"
                f"不能直接跳转到「{label(new)}」"
            )

    @staticmethod
    def assert_revert(old: int, target: int) -> None:
        """反向跳转（撤销）校验。"""
        valid = TASK_REVERSE_TRANS.get(old, set())
        if target not in valid:
            raise BizException(
                f"不允许的回退路径：「{label(old)}」 → 「{label(target)}」"
            )

    @staticmethod
    def assert_force_cancellable(old: int) -> None:
        """强制取消（线下取消）入口校验。"""
        if old not in TASK_FORCE_CANCEL_FROM:
            raise BizException(
                "仅「已装车 / 在途 / 已到达」可强制取消；"
                "「已签收 / 已关闭」请走客户差异处理流程"
            )

    @staticmethod
    def assert_cancellable(old: int) -> None:
        """常规取消（仅 status ≤ 2，与既有 cancel_task 行为一致）"""
        if old not in TASK_CANCEL_FROM:
            raise BizException(
                f"任务单状态「{label(old)}」不允许取消"
            )

    @staticmethod
    def legal_next(old: int) -> Set[int]:
        return set(TASK_VALID_TRANS.get(old, set()))

    @staticmethod
    def legal_revert(old: int) -> Set[int]:
        return set(TASK_REVERSE_TRANS.get(old, set()))

    @staticmethod
    def can_force_cancel(old: int) -> bool:
        return old in TASK_FORCE_CANCEL_FROM
