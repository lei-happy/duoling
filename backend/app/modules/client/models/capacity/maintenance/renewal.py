"""
保险 / 年检续期台账（租户库）

生效后回写 vehicle_ext 到期日，并关闭对应证照告警。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetRenewal(TenantModelBase):
    """续期台账

    renewal_type: insurance | inspection
    status: draft | effective | cancelled
    """

    __tablename__ = "biz_fleet_renewal"
    __table_args__ = (
        Index("idx_fleet_renewal_vehicle_type", "vehicle_id", "renewal_type"),
        Index("idx_fleet_renewal_status_eff", "status", "effective_date"),
        {"comment": "车辆保险/年检续期台账"},
    )
    __table_tier__ = "business"

    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="车辆ID"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号（冗余）"
    )
    renewal_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="类型 insurance/inspection"
    )
    effective_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="生效日"
    )
    expire_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="新到期日"
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="费用金额"
    )
    policy_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="保单号（保险）"
    )
    attachment_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="附件地址"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", comment="状态"
    )
    effective_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="生效操作时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
