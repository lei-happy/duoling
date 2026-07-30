"""车辆资产 - 维修保养 / 续期模型"""

from app.modules.client.models.capacity.maintenance.work_order import FleetWorkOrder
from app.modules.client.models.capacity.maintenance.maintain_plan import FleetMaintainPlan
from app.modules.client.models.capacity.maintenance.renewal import FleetRenewal

__all__ = [
    "FleetWorkOrder",
    "FleetMaintainPlan",
    "FleetRenewal",
]
