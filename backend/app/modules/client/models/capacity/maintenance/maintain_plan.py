"""
保养计划表（租户库）

按时间 / 里程 / 孰先到期配置预防性保养规则。
"""

from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Date, Index, Integer, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetMaintainPlan(TenantModelBase):
    """保养计划

    cycle_type: time | mileage | either
    """

    __tablename__ = "biz_fleet_maintain_plan"
    __table_args__ = (
        Index("idx_fleet_plan_vehicle_enabled", "vehicle_id", "enabled"),
        {"comment": "车辆保养计划表"},
    )
    __table_tier__ = "business"

    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="车辆ID"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号（冗余）"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="计划名称"
    )
    cycle_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="周期类型 time/mileage/either"
    )
    interval_days: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="时间间隔（天）"
    )
    interval_mileage: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="里程间隔（km）"
    )
    last_maintain_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="上次保养日"
    )
    last_maintain_mileage: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="上次保养里程"
    )
    next_maintain_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="下次保养日（缓存）"
    )
    next_maintain_mileage: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="下次保养里程（缓存）"
    )
    remind_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=7, server_default=text("7"),
        comment="提前提醒天数",
    )
    enabled: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="是否启用 1-是 0-否",
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
