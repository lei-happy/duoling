"""三层业务状态机抽象

集中维护 Task / Waybill / TaskWaybillItem 三类业务单据的状态机定义。
状态机本身不依赖任何 ORM 或会话；service 层在状态变更前后调用其中的
`assert_*` 工具方法做合法性校验。

设计参考：项目文档/02.需求文档/02.企业端/06.运营调度模块/
        02.运单与任务单状态机联动设计.md
"""

from app.modules.client.services.state_machine.task_state_machine import (
    TASK_FORCE_CANCEL_FROM,
    TASK_REVERSE_TRANS,
    TASK_STATUS_LABELS,
    TASK_VALID_TRANS,
    TaskStateMachine,
)
from app.modules.client.services.state_machine.waybill_state_machine import (
    WAYBILL_STATUS_LABELS,
    WAYBILL_VALID_TRANS,
    WaybillStateMachine,
)
from app.modules.client.services.state_machine.item_state_machine import (
    ITEM_STATUS_LABELS,
    ITEM_VALID_TRANS,
    ItemStateMachine,
)
from app.modules.client.services.state_machine.dispatch_order_state_machine import (
    CARGO_DISPATCH_TYPES,
    DISPATCH_ORDER_NO_MAX,
    DISPATCH_ORDER_NO_MIN,
    DISPATCH_ORDER_STATUS_LABELS,
    DISPATCH_ORDER_STATUS_MAX,
    DISPATCH_ORDER_STATUS_MIN,
    DISPATCH_TYPE_DEFAULT,
    DISPATCH_TYPE_HEAVY,
    DISPATCH_TYPE_LABELS,
    DISPATCH_TYPE_MAX,
    DISPATCH_TYPE_MIN,
    DISPATCH_PENDING_LOAD,
    MAIN_LINE_ORDER_NO,
    is_valid_dispatch_order_status,
    is_valid_dispatch_type,
)

__all__ = [
    "TASK_FORCE_CANCEL_FROM",
    "TASK_REVERSE_TRANS",
    "TASK_STATUS_LABELS",
    "TASK_VALID_TRANS",
    "TaskStateMachine",
    "WAYBILL_STATUS_LABELS",
    "WAYBILL_VALID_TRANS",
    "WaybillStateMachine",
    "ITEM_STATUS_LABELS",
    "ITEM_VALID_TRANS",
    "ItemStateMachine",
    "CARGO_DISPATCH_TYPES",
    "DISPATCH_ORDER_NO_MAX",
    "DISPATCH_ORDER_NO_MIN",
    "DISPATCH_ORDER_STATUS_LABELS",
    "DISPATCH_ORDER_STATUS_MAX",
    "DISPATCH_ORDER_STATUS_MIN",
    "DISPATCH_TYPE_DEFAULT",
    "DISPATCH_TYPE_HEAVY",
    "DISPATCH_TYPE_LABELS",
    "DISPATCH_TYPE_MAX",
    "DISPATCH_TYPE_MIN",
    "DISPATCH_PENDING_LOAD",
    "MAIN_LINE_ORDER_NO",
    "is_valid_dispatch_order_status",
    "is_valid_dispatch_type",
]
