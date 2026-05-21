"""运单状态机

Waybill.status 状态空间（客户视角的"票据流转"）：
    0 待确认（新建运单后，等运营/客户点击「确认」推进到 1）
    1 待调度（已确认，等待挂入任务单）
    2 调度中（部分或全部 cargo 行已挂入未取消的任务单）
    3 运输中（至少一行 item 已装车）
    4 待签收（聚合门槛：全量货物已到达）
    5 已签收（聚合门槛：全量货物已签收，对客户即"流程闭环"）
    6 已关闭（终态，可在任意非草稿状态进入）

Waybill 状态由聚合器 ``WaybillStatusAggregator`` 推导，不应由用户直接传值；
仍保留 ``update_status`` API 用于运营兜底（例如手动确认、手动关闭），但需经状态机校验。

文案设计原因（2026-05 调整）：
- 4 由"已送达"改"待签收"：强调签收是运单维度的客户动作，与任务单的"已到达"区分；
- 5 由"已完成"改"已签收"：保持与 item.status=3 一致，避免歧义。
- 数值不变；前端、后端文案统一。
"""

from typing import Set

from app.common.exceptions import BizException


# —— 状态值常量（新命名 + 旧别名）
WAYBILL_PENDING_CONFIRM = 0  # 待确认（运单新建后初始态）
WAYBILL_PENDING = 1          # 待调度
WAYBILL_SCHEDULING = 2       # 调度中
WAYBILL_IN_TRANSIT = 3       # 运输中
WAYBILL_PENDING_SIGN = 4     # 待签收
WAYBILL_SIGNED = 5           # 已签收
WAYBILL_CLOSED = 6           # 已关闭

# 旧别名（兼容历史 import；如 waybill_status_aggregator）
WAYBILL_DRAFT = WAYBILL_PENDING_CONFIRM
WAYBILL_DELIVERED = WAYBILL_PENDING_SIGN
WAYBILL_COMPLETED = WAYBILL_SIGNED


WAYBILL_STATUS_LABELS: dict[int, str] = {
    0: "待确认",
    1: "待调度",
    2: "调度中",
    3: "运输中",
    4: "待签收",
    5: "已签收",
    6: "已关闭",
}


# 正向 + 反向合一的合法跳转（聚合器内部会按需正/反向推进）
#
# 设计要点：
# 聚合器是 waybill 状态的**唯一权威来源**，多个 task 装/卸车场景下需要
# 跨步跳转（例如 1 待调度的运单被一次性拉到 3 运输中：等价于
# "1→2→3 一步合并执行"）。如果将 valid_trans 限制为单步邻接，
# 历史数据回填或并发场景将导致 ``assert_transition`` 抛错并使整个
# 装/卸车事务回滚。
#
# 因此正向方向（"待调度/调度中"两个低位态）允许直接跨步跳到任意活跃态；
# 高位态之间仍保持严格相邻（避免数据异常时静默放过）。
WAYBILL_VALID_TRANS: dict[int, Set[int]] = {
    0: {1, 6},
    1: {2, 3, 4, 5, 6},   # 待调度允许由聚合器跨步推进至任意活跃态
    2: {1, 3, 4, 5, 6},   # 调度中同上（含回退到待调度）
    3: {2, 4, 5, 6},      # 运输中可回退到调度中 / 跨步至已签收（全量装车后立即签收）
    4: {3, 5, 6},         # 待签收可回退到运输中（撤销到达）
    5: {4, 6},            # 已签收可回退到待签收（撤销签收）
    6: set(),             # 已关闭终态
}


# 已挂接活跃任务时，不允许的用户操作目标
# （删除运单、回到草稿/待调度等）
WAYBILL_STATES_BLOCKING_DELETE: Set[int] = {2, 3, 4, 5}


# 禁止新挂接的运单态（>=4 待签收起，不再允许新任务挂接）
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
