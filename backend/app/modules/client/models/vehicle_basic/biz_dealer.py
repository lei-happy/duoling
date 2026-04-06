"""
租户经销商表（开户时从平台 basicdata_dealer_info 同步）
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, BigInteger, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TenantBase


class BizDealer(TenantBase):
    __tablename__ = "biz_dealer"
    __table_args__ = {"comment": "汽车经销商信息表"}
    __table_tier__ = "core"

    dealer_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="经销商ID"
    )
    dealer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dealer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    main_brand: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    address_detail: Mapped[str] = mapped_column(String(255), nullable=False)
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True
    )
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
