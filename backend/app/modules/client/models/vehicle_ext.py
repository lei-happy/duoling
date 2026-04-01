"""
车辆扩展信息表（租户库）

与 biz_vehicle 1:1 关联，存储可扩展的详细属性字段。
后期新增字段只需修改此表，核心表保持稳定。
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, BigInteger, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class VehicleExt(TenantModelBase):
    """车辆扩展信息"""
    __tablename__ = "biz_vehicle_ext"
    __table_args__ = {"comment": "车辆扩展信息表"}
    __table_tier__ = "business"

    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, comment="关联车辆ID"
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
    load_capacity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定载重（吨）"
    )
    volume_capacity: Mapped[Optional[float]] = mapped_column(
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
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
