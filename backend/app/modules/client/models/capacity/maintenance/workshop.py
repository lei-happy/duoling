"""维修厂主数据"""

from typing import Optional

from sqlalchemy import Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetWorkshop(TenantModelBase):
    """维修厂"""

    __tablename__ = "biz_fleet_workshop"
    __table_args__ = (
        Index("idx_fleet_workshop_enabled", "enabled"),
        {"comment": "车辆维修厂主数据"},
    )
    __table_tier__ = "business"

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="名称"
    )
    contact: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="联系人"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="电话"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="地址"
    )
    enabled: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="是否启用",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
