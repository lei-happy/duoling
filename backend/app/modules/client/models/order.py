"""
运单/订单表（租户库）
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Order(TenantModelBase):
    """运单"""
    __tablename__ = "biz_order"
    __table_args__ = {"comment": "运单表"}
    __table_tier__ = "business"

    order_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="运单号"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="客户ID"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称"
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="车辆ID"
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号"
    )
    driver_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="驾驶员ID"
    )
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="驾驶员姓名"
    )
    route_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="路线ID"
    )
    origin: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="起点"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="终点"
    )
    cargo_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="货物名称"
    )
    cargo_weight: Mapped[Optional[str]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="货物重量（吨）"
    )
    cargo_volume: Mapped[Optional[str]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="货物体积（立方米）"
    )
    freight_amount: Mapped[Optional[str]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="运费金额"
    )
    plan_depart_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划发车时间"
    )
    actual_depart_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际发车时间"
    )
    plan_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划到达时间"
    )
    actual_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际到达时间"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0,
        comment="状态 0-待派车 1-已派车 2-运输中 3-已到达 4-已签收 5-已完成 6-已取消"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
