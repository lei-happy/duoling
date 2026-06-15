"""
承运商运力 - 车辆详情表（租户库）

与 biz_carrier_capacity 1:1 关联。字段与社会运力车辆详情对称，
便于证照监控引擎统一扫描（inspection_expire / insurance_expire /
transport_license_expire 等字段命名保持一致）。
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, SmallInteger, BigInteger, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CarrierCapacityVehicle(TenantModelBase):
    """承运商运力车辆详情"""

    __tablename__ = "biz_carrier_capacity_vehicle"
    __table_args__ = {"comment": "承运商运力车辆详情表"}
    __table_tier__ = "business"

    carrier_capacity_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, comment="关联 biz_carrier_capacity.id"
    )

    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号"
    )
    plate_category: Mapped[str] = mapped_column(
        String(20),
        default="YELLOW",
        server_default="YELLOW",
        nullable=False,
        comment="车牌类型 BLUE/YELLOW/NEW_ENERGY",
    )
    vehicle_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="车辆类型（数据字典 vehicle_type）"
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
        String(50), nullable=True, comment="车架号 VIN"
    )
    engine_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发动机号"
    )

    # 规格
    load_capacity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定载重（吨）"
    )
    volume_capacity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定容积（立方米）"
    )
    length: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="长度（米）"
    )
    width: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="宽度（米）"
    )
    height: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="高度（米）"
    )
    axle_count: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="轴数"
    )

    # 挂车（轻量内嵌）
    has_trailer: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default="0",
        nullable=False,
        comment="是否含挂车 0-否 1-是",
    )
    trailer_plate: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="挂车车牌号"
    )
    trailer_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="挂车类型（数据字典 trailer_type）"
    )
    trailer_load_capacity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="挂车核定载重（吨）"
    )

    # 资质
    registration_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="注册日期"
    )
    inspection_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="年检到期日"
    )
    insurance_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="保险到期日"
    )
    transport_license_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="道路运输证号"
    )
    transport_license_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="道路运输证有效期"
    )

    # 证照影像
    vehicle_license_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="行驶证主页 URL"
    )
    vehicle_license_back_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="行驶证副页 URL"
    )
    transport_license_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="道路运输证照片 URL"
    )
    vehicle_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="车辆外观照 URL"
    )
