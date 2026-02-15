"""
车辆管理表（租户库）
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, SmallInteger, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Vehicle(TenantModelBase):
    """车辆信息"""
    __tablename__ = "biz_vehicle"
    __table_args__ = {"comment": "车辆信息表"}

    plate_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="车牌号"
    )
    vehicle_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="车辆类型（如重型货车、轻型货车等）"
    )
    brand: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="品牌"
    )
    model: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="型号"
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="颜色"
    )
    vin: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="车架号(VIN)"
    )
    engine_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发动机号"
    )
    load_capacity: Mapped[Optional[str]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定载重（吨）"
    )
    volume_capacity: Mapped[Optional[str]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定容积（立方米）"
    )
    purchase_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="购买日期"
    )
    insurance_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="保险到期日"
    )
    inspection_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="年检到期日"
    )
    gps_device_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="GPS设备ID"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常 2-维修中 3-已报废"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
