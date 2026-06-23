"""任务单调令（TaskDispatchOrder）类型与状态常量

调令 = 任务下"一段完整运输运动"，承担调度归属与成本归集的最小单元。
本模块集中维护：

- 调令类型 ``dispatch_type``（重驶 / 空驶 / 年检 / 应急 / 其他）
- 调令状态 ``status``（待装车 → 装车中 → 在途 → 已到达 → 已卸车）

目的：避免业务代码中散落魔法数字（如 ``dispatch_type == 1`` 判定"重驶"、
``status in (0, 1, 2, 3, 4)`` 判定合法状态），统一由常量驱动。

设计参考：项目文档/02.需求文档/02.企业端/06.运营调度模块/
        03.任务单调令设计.md
"""

# ==========================================================
# 调令类型 dispatch_type
# ==========================================================
DISPATCH_TYPE_HEAVY = 1        # 重驶：拉着商品车的实际运输段（带货主业务段）
DISPATCH_TYPE_EMPTY = 2        # 空驶：空车回程 / 调拨段（不带货，归属任务作为成本）
DISPATCH_TYPE_INSPECTION = 3   # 年检：车辆年检调拨
DISPATCH_TYPE_EMERGENCY = 4    # 应急：应急调拨（事故 / 抢救）
DISPATCH_TYPE_OTHER = 5        # 其他：其他业务调拨


DISPATCH_TYPE_LABELS: dict[int, str] = {
    DISPATCH_TYPE_HEAVY: "重驶",
    DISPATCH_TYPE_EMPTY: "空驶",
    DISPATCH_TYPE_INSPECTION: "年检",
    DISPATCH_TYPE_EMERGENCY: "应急",
    DISPATCH_TYPE_OTHER: "其他",
}

DISPATCH_TYPE_MIN = DISPATCH_TYPE_HEAVY
DISPATCH_TYPE_MAX = DISPATCH_TYPE_OTHER

# 默认调令类型（未指定时按"重驶"处理）
DISPATCH_TYPE_DEFAULT = DISPATCH_TYPE_HEAVY

# 带货（需要装卸 / 可承载商品车）的调令类型：当前仅"重驶"
CARGO_DISPATCH_TYPES: set[int] = {DISPATCH_TYPE_HEAVY}


# ==========================================================
# 调令状态 status
# ==========================================================
DISPATCH_PENDING_LOAD = 0  # 待装车
DISPATCH_LOADING = 1       # 装车中
DISPATCH_ON_WAY = 2        # 在途
DISPATCH_ARRIVED = 3       # 已到达
DISPATCH_UNLOADED = 4      # 已卸车


DISPATCH_ORDER_STATUS_LABELS: dict[int, str] = {
    DISPATCH_PENDING_LOAD: "待装车",
    DISPATCH_LOADING: "装车中",
    DISPATCH_ON_WAY: "在途",
    DISPATCH_ARRIVED: "已到达",
    DISPATCH_UNLOADED: "已卸车",
}

DISPATCH_ORDER_STATUS_MIN = DISPATCH_PENDING_LOAD
DISPATCH_ORDER_STATUS_MAX = DISPATCH_UNLOADED


# ==========================================================
# 调令序号
# ==========================================================
# 调令序号取值范围（与前端规划路线子表上限保持一致）
DISPATCH_ORDER_NO_MIN = 1
DISPATCH_ORDER_NO_MAX = 20

# "主线路"调令序号：未手动规划路线时，按任务起终点自动生成的首条重驶调令
MAIN_LINE_ORDER_NO = 1


def is_valid_dispatch_type(value: int) -> bool:
    return value in DISPATCH_TYPE_LABELS


def is_valid_dispatch_order_status(value: int) -> bool:
    return value in DISPATCH_ORDER_STATUS_LABELS


def dispatch_type_label(value: int) -> str:
    return DISPATCH_TYPE_LABELS.get(value, str(value))


def dispatch_order_status_label(value: int) -> str:
    return DISPATCH_ORDER_STATUS_LABELS.get(value, str(value))
