"""能源商品（租户库）"""

from typing import Optional

from sqlalchemy import Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyProduct(TenantModelBase):
    """能源商品（0#柴油 / LNG / 充电等）"""

    __tablename__ = "biz_energy_product"
    __table_args__ = (
        Index("uk_energy_product_code", "product_code", unique=True),
        {"comment": "能源商品表"},
    )
    __table_tier__ = "business"

    energy_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="能源类型 OIL/GAS/ELECTRIC/OTHER"
    )
    product_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="商品编码（租户内唯一）"
    )
    product_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="商品名称"
    )
    standard_unit: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="标准单位 L/kg/m3/kWh"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
