"""车辆资产 - 维修保养 / 续期 / 备件模型"""

from app.modules.client.models.capacity.maintenance.work_order import FleetWorkOrder
from app.modules.client.models.capacity.maintenance.work_order_line import (
    FleetWorkOrderLine,
)
from app.modules.client.models.capacity.maintenance.maintain_plan import (
    FleetMaintainPlan,
)
from app.modules.client.models.capacity.maintenance.renewal import FleetRenewal
from app.modules.client.models.capacity.maintenance.part import FleetPart
from app.modules.client.models.capacity.maintenance.stock_txn import FleetStockTxn
from app.modules.client.models.capacity.maintenance.workshop import FleetWorkshop

__all__ = [
    "FleetWorkOrder",
    "FleetWorkOrderLine",
    "FleetMaintainPlan",
    "FleetRenewal",
    "FleetPart",
    "FleetStockTxn",
    "FleetWorkshop",
]
