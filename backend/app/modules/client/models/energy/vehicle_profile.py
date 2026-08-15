"""车辆能源档案（租户库）

运输车辆自身的燃料类型 / 油箱容量等，与运力模块解耦：不改 biz_vehicle_ext。
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyVehicleProfile(TenantModelBase):
    """车辆能源档案"""

    __tablename__ = "biz_energy_vehicle_profile"
    __table_args__ = (
        Index("uk_energy_vehicle_profile", "vehicle_id", unique=True),
        {"comment": "车辆能源档案表"},
    )
    __table_tier__ = "business"

    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="车辆 ID（biz_vehicle.id）"
    )
    energy_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="能源类型 OIL/GAS/ELECTRIC/OTHER"
    )
    default_product_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="默认能源商品 ID"
    )
    tank_capacity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="油箱/气瓶容量（L 或 kg）"
    )
    battery_capacity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="电池容量（kWh）"
    )
    standard_consumption_per_100km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="标准百公里能耗"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
