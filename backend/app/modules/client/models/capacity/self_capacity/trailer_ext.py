"""
挂车扩展信息表（租户库）

与 biz_trailer 1:1 关联，存储可扩展的详细属性字段。
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, SmallInteger, BigInteger, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TrailerExt(TenantModelBase):
    """挂车扩展信息"""
    __tablename__ = "biz_trailer_ext"
    __table_args__ = {"comment": "挂车扩展信息表"}
    __table_tier__ = "business"

    trailer_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, comment="关联挂车ID"
    )
    trailer_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="挂车类型（数据字典 trailer_type）"
    )
    axle_count: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="轴数"
    )
    load_capacity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定载重（吨）"
    )
    volume_capacity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定容积（立方米）"
    )
    length: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="车厢长度（米）"
    )
    width: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="车厢宽度（米）"
    )
    height: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="车厢高度（米）"
    )
    parking_spots: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="车位数"
    )
    purchase_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="购买日期"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
