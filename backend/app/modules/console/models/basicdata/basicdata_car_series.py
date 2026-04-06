"""
平台库车系表 basicdata_car_series
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class BasicdataCarSeries(PlatformBase):
    __tablename__ = "basicdata_car_series"
    __table_args__ = {"comment": "车系信息表", "extend_existing": True}

    series_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="车系ID"
    )
    brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("basicdata_brand.brand_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    price: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    series_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    series_name: Mapped[str] = mapped_column(String(100), nullable=False)
    energy_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    length_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wheelbase_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    front_track_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rear_track_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    approach_angle: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    departure_angle: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    curb_weight_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
