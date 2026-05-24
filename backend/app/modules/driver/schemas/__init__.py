"""驾驶员端 Schemas"""

from app.modules.driver.schemas.task import (
    DriverConfirmLoadRequest,
    DriverDepartRequest,
    DriverConfirmArriveRequest,
    DriverSignItemRequest,
    DriverRevertSignRequest,
    DriverTaskListItem,
    DriverTaskDetail,
    DriverTaskItem,
)
from app.modules.driver.schemas.finance import (
    DriverFinanceListItem,
    DriverFinanceDetail,
    DriverFinanceItemOut,
    DriverFinanceSummary,
    DriverAccountOut,
)
from app.modules.driver.schemas.profile import (
    DriverProfileOut,
    DriverProfileUpdate,
)

__all__ = [
    "DriverConfirmLoadRequest",
    "DriverDepartRequest",
    "DriverConfirmArriveRequest",
    "DriverSignItemRequest",
    "DriverRevertSignRequest",
    "DriverTaskListItem",
    "DriverTaskDetail",
    "DriverTaskItem",
    "DriverFinanceListItem",
    "DriverFinanceDetail",
    "DriverFinanceItemOut",
    "DriverFinanceSummary",
    "DriverAccountOut",
    "DriverProfileOut",
    "DriverProfileUpdate",
]
