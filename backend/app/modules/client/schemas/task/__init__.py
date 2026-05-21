"""任务单相关 Schemas 统一导出"""

from app.modules.client.schemas.task.task import (
    TaskCarrierInfo,
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskAssignCarrierRequest,
    TaskCancelRequest,
    TaskListItemOut,
    TaskOut,
)
from app.modules.client.schemas.task.task_dispatch_order import (
    TaskDispatchOrderIn,
    TaskDispatchOrderStatusUpdate,
    TaskDispatchOrderOut,
)
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemIn,
    TaskWaybillItemStatusUpdate,
    TaskWaybillItemOut,
    CandidateCargoOut,
)
from app.modules.client.schemas.task.task_loading_record import (
    TaskLoadingRecordCreate,
    TaskLoadingRecordItemIn,
    TaskLoadingRecordItemOut,
    TaskLoadingRecordOut,
)
from app.modules.client.schemas.task.task_finance_doc import (
    TaskFinanceDocCreate,
    TaskFinanceDocUpdate,
    TaskFinanceDocPayRequest,
    TaskFinanceDocCancelRequest,
    TaskFinanceDocOut,
    TaskFinanceDocListItem,
)
from app.modules.client.schemas.task.task_finance_item import (
    TaskFinanceItemIn,
    TaskFinanceItemOut,
)

__all__ = [
    # task
    "TaskCarrierInfo",
    "TaskCreate",
    "TaskUpdate",
    "TaskStatusUpdate",
    "TaskAssignCarrierRequest",
    "TaskCancelRequest",
    "TaskListItemOut",
    "TaskOut",
    # dispatch order（原 segment）
    "TaskDispatchOrderIn",
    "TaskDispatchOrderStatusUpdate",
    "TaskDispatchOrderOut",
    # waybill item
    "TaskWaybillItemIn",
    "TaskWaybillItemStatusUpdate",
    "TaskWaybillItemOut",
    "CandidateCargoOut",
    # loading record
    "TaskLoadingRecordCreate",
    "TaskLoadingRecordItemIn",
    "TaskLoadingRecordItemOut",
    "TaskLoadingRecordOut",
    # finance doc
    "TaskFinanceDocCreate",
    "TaskFinanceDocUpdate",
    "TaskFinanceDocPayRequest",
    "TaskFinanceDocCancelRequest",
    "TaskFinanceDocOut",
    "TaskFinanceDocListItem",
    # finance item
    "TaskFinanceItemIn",
    "TaskFinanceItemOut",
]
