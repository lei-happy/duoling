"""
车辆核心表（租户库）

仅保留业务必须字段，详细属性存储在扩展表 biz_vehicle_ext 中。
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Vehicle(TenantModelBase):
    """车辆核心信息"""
    __tablename__ = "biz_vehicle"
    __table_args__ = {"comment": "车辆核心表"}
    __table_tier__ = "business"

    plate_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="车牌号"
    )
    trailer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联挂车ID"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1,
        comment="状态 0-停用 1-正常 2-维修/保养 3-保险续期 9-已报废"
    )
    status_source: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default="manual",
        comment="状态变更来源（manual/maintenance/insurance）"
    )
