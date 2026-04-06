"""
租户品牌表（开户时从平台 basicdata_brand 同步）
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TenantBase


class BizVehicleBrand(TenantBase):
    __tablename__ = "biz_vehicle_brand"
    __table_args__ = {"comment": "品牌信息表"}
    __table_tier__ = "core"

    brand_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="品牌ID（主键）"
    )
    brand_logo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="品牌Logo路径或链接"
    )
    brand_name_cn: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="品牌中文名称"
    )
    brand_country: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="品牌国别"
    )
    brand_introduce: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="品牌介绍"
    )
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    last_update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="最后更新时间",
    )
