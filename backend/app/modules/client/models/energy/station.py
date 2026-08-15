"""能源站点（租户库）"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyStation(TenantModelBase):
    """能源站点"""

    __tablename__ = "biz_energy_station"
    __table_args__ = (
        Index("idx_energy_station_supplier", "supplier_id"),
        Index("uk_energy_station_code", "supplier_id", "station_code", unique=True),
        {"comment": "能源站点表"},
    )
    __table_tier__ = "business"

    supplier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="供应商 ID"
    )
    station_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="站点编码（供应商内唯一）"
    )
    station_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="站点名称"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="地址"
    )
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True, comment="经度"
    )
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True, comment="纬度"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
