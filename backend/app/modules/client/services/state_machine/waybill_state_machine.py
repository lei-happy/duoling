"""计划状态机（与任务状态机彼此独立的"计划域"权威）

Waybill.status 状态空间（客户视角的"票据流转"）：
    0 待确认（新建计划后，等运营/客户点击「确认」推进到 1）
    1 待调度（已确认，等待挂入任务单）
    2 调度中（部分或全部 cargo 行已挂入未取消的任务单）
    3 运输中（至少一行 item 已装车）
    4 待交车（聚合门槛：全量货物已到达）
    5 已交车（聚合门槛：全量货物已交车，对客户即"车已交付"）
    6 已回单（人工动作：交车回单返还货主，计划对货主的真正闭环）
    7 已关闭（终态，可在任意非草稿状态进入）

驱动边界（独立性约束，详见《02.计划与任务单状态机联动设计.md》与方案）：
- ``1..5`` 由聚合器 ``WaybillStatusAggregator`` 从挂接 item 进度单向推导，不由用户直接传值；
- ``6 已回单`` / ``7 已关闭`` 为计划侧人工动作（``update_status`` / ``WaybillReceiptService``），
  聚合器 **skip 不自动改写**，与任务状态机完全无关；
- 计划状态**永不回写任务**；任务侧只读展示其下计划状态分布。

文案设计原因：
- 2026-05：4 由"已送达"改"待签收"；5 由"已完成"改"已签收"，与 item.status=3 对齐。
- 2026-06：新增 6 已回单，原 6 已关闭整体后移为 7（保持数值单调，便于聚合器 max 比较）。
- 2026-08：4/5 文案再调整为"待交车/已交车"，与商品车运输行业口径统一（任务域同步）。
  **仅文案变更**：状态值、跳转表、聚合规则与任务状态机的独立性均不受影响；
  常量名 ``WAYBILL_PENDING_SIGN`` / ``WAYBILL_SIGNED`` 保持不变，避免波及历史 import。
"""

from typing import Set

from app.common.exceptions import BizException


# —— 状态值常量（新命名 + 旧别名）
WAYBILL_PENDING_CONFIRM = 0  # 待确认（计划新建后初始态）
WAYBILL_PENDING = 1          # 待调度
WAYBILL_SCHEDULING = 2       # 调度中
WAYBILL_IN_TRANSIT = 3       # 运输中
WAYBILL_PENDING_SIGN = 4     # 待交车
WAYBILL_SIGNED = 5           # 已交车
WAYBILL_RECEIPTED = 6        # 已回单（人工：交车回单返还货主）
WAYBILL_CLOSED = 7           # 已关闭（原 6，整体后移）

# 旧别名（兼容历史 import；如 waybill_status_aggregator）
WAYBILL_DRAFT = WAYBILL_PENDING_CONFIRM
WAYBILL_DELIVERED = WAYBILL_PENDING_SIGN
WAYBILL_COMPLETED = WAYBILL_SIGNED


WAYBILL_STATUS_LABELS: dict[int, str] = {
    0: "待确认",
    1: "待调度",
    2: "调度中",
    3: "运输中",
    4: "待交车",
    5: "已交车",
    6: "已回单",
    7: "已关闭",
}


# 正向 + 反向合一的合法跳转（聚合器内部会按需正/反向推进）
#
# 设计要点：
# 聚合器是 waybill 状态的**唯一权威来源**，多个 task 装/卸车场景下需要
# 跨步跳转（例如 1 待调度的计划被一次性拉到 3 运输中：等价于
# "1→2→3 一步合并执行"）。如果将 valid_trans 限制为单步邻接，
# 历史数据回填或并发场景将导致 ``assert_transition`` 抛错并使整个
# 装/卸车事务回滚。
#
# 因此正向方向（"待调度/调度中"两个低位态）允许直接跨步跳到任意活跃态。
# 反向同样允许跨步回退到更低作业态：整单取消 / 强制取消后无活跃挂接时，
# 聚合器会把计划一次性拉回「待调度」，避免误操作把计划卡死在运输中/待交车。
# 「已回单」仍必须先撤销回单（6→5），「已关闭」终态不可回退。
WAYBILL_VALID_TRANS: dict[int, Set[int]] = {
    0: {1, 7},
    1: {2, 3, 4, 5, 7},          # 待调度允许由聚合器跨步推进至任意活跃态
    2: {1, 3, 4, 5, 7},          # 调度中同上（含回退到待调度）
    3: {1, 2, 4, 5, 7},          # 运输中：撤销装车→调度中；整单取消→待调度
    4: {1, 2, 3, 5, 7},          # 待交车：撤销到达 / 取消后无挂接
    5: {1, 2, 3, 4, 6, 7},       # 已交车：撤销交车逐步回退，或取消后回到待调度
    6: {5, 7},                   # 已回单 → 撤销回单回退已交车 / 关闭
    7: set(),                    # 已关闭终态
}


# 已挂接活跃任务时，不允许的用户操作目标
# （删除计划、回到草稿/待调度等）
WAYBILL_STATES_BLOCKING_DELETE: Set[int] = {2, 3, 4, 5, 6}


# 禁止新挂接的计划态（>=4 待交车起，不再允许新任务挂接）
WAYBILL_STATES_BLOCKING_NEW_ITEM: Set[int] = {4, 5, 6, 7}


def label(status: int) -> str:
    return WAYBILL_STATUS_LABELS.get(status, str(status))


class WaybillStateMachine:
    """计划状态机工具方法"""

    @staticmethod
    def assert_transition(old: int, new: int) -> None:
        """统一跳转校验。正/反向都用同一张表，由聚合器保证语义。"""
        if old == new:
            return
        valid = WAYBILL_VALID_TRANS.get(old, set())
        if new not in valid:
            raise BizException(
                f"计划状态从「{label(old)}」"
                f"不能跳转到「{label(new)}」"
            )

    @staticmethod
    def allows_new_item(status: int) -> bool:
        """计划是否允许新增任务挂接（waybillItems）"""
        return status not in WAYBILL_STATES_BLOCKING_NEW_ITEM

    @staticmethod
    def allows_delete(status: int, has_active_task_items: bool) -> bool:
        """计划是否允许删除/编辑核心字段：状态 ≤ 待调度 且 无活跃挂接"""
        if status in WAYBILL_STATES_BLOCKING_DELETE:
            return False
        if has_active_task_items:
            return False
        return True

    @staticmethod
    def is_terminal(status: int) -> bool:
        return status == WAYBILL_CLOSED
