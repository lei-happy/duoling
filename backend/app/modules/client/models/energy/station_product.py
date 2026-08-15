"""能源站点可加注商品及供应商结算价（租户库）

一期只存当前结算价，不记历史。调价直接改本行。
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyStationProduct(TenantModelBase):
    """站点商品结算价"""

    __tablename__ = "biz_energy_station_product"
    __table_args__ = (
        Index("idx_energy_station_product_station", "station_id"),
        Index(
            "uk_energy_station_product",
            "station_id", "energy_type", "product_id",
            unique=True,
        ),
        {"comment": "能源站点商品结算价"},
    )
    __table_tier__ = "business"

    station_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="站点 ID"
    )
    energy_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="能源类型 OIL/GAS/ELECTRIC/OTHER"
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default=text("0"),
        comment="能源商品 ID，0 表示按能源类型定价",
    )
    product_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="商品名称快照"
    )
    settlement_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, comment="供应商结算单价"
    )
    unit: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="计价单位 L/kg/kWh"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
