"""自有运力模型：车辆 / 挂车 / 驾驶员 / 司机-车辆绑定"""

from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.capacity.self_capacity.trailer import Trailer
from app.modules.client.models.capacity.self_capacity.trailer_ext import TrailerExt
from app.modules.client.models.capacity.self_capacity.capacity import (
    Capacity,
    CapacityLog,
)
from app.modules.client.models.capacity.self_capacity.capacity_group import (
    CapacityGroup,
    CapacityGroupMember,
)
from app.modules.client.models.capacity.self_capacity.driver import (
    Driver,
    DriverLicense,
    DriverOperation,
    DriverAccount,
    DriverRoute,
)

__all__ = [
    "Vehicle",
    "VehicleExt",
    "Trailer",
    "TrailerExt",
    "Capacity",
    "CapacityLog",
    "CapacityGroup",
    "CapacityGroupMember",
    "Driver",
    "DriverLicense",
    "DriverOperation",
    "DriverAccount",
    "DriverRoute",
]
