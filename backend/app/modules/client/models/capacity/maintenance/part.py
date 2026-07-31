"""备件主数据（租户级轻量库存）"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetPart(TenantModelBase):
    """备件主数据

    status: 1-启用 0-停用
    """

    __tablename__ = "biz_fleet_part"
    __table_args__ = (
        UniqueConstraint("part_code", name="uk_fleet_part_code"),
        Index("idx_fleet_part_status_name", "status", "part_name"),
        {"comment": "车辆备件主数据"},
    )
    __table_tier__ = "business"

    part_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="备件编码"
    )
    part_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="备件名称"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="分类"
    )
    unit: Mapped[str] = mapped_column(
        String(20), nullable=False, default="个",
        server_default=text("'个'"), comment="单位",
    )
    ref_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="参考单价"
    )
    safety_stock: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="安全库存",
    )
    qty_on_hand: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0, server_default=text("0"),
        comment="现存量",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="1启用 0停用",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
