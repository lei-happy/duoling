"""
维保工单表（租户库）

维修 / 保养作业闭环单据；开工/完工驱动车辆与运力状态。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetWorkOrder(TenantModelBase):
    """维保工单

    order_type: repair | maintenance
    status: draft | in_progress | completed | cancelled
    """

    __tablename__ = "biz_fleet_work_order"
    __table_args__ = (
        UniqueConstraint("work_order_no", name="uk_fleet_wo_no"),
        Index("idx_fleet_wo_vehicle_status", "vehicle_id", "status"),
        Index("idx_fleet_wo_status_updated", "status", "updated_at"),
        {"comment": "车辆维保工单表"},
    )
    __table_tier__ = "business"

    work_order_no: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="工单号"
    )
    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="车辆ID"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号（冗余）"
    )
    order_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="类型 repair/maintenance"
    )
    plan_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联保养计划ID"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="标题/故障简述"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="详细说明"
    )
    odometer: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="进厂里程(km)"
    )
    workshop: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="维修厂/地点"
    )
    expect_finish_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="预计完工日"
    )
    cost_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="费用合计"
    )
    cost_remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="费用明细备注"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", comment="状态"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开工时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完工/取消时间"
    )
    capacity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="开工时锁定的运力ID"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
