"""
平台库品牌表 basicdata_brand
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class BasicdataBrand(PlatformBase):
    __tablename__ = "basicdata_brand"
    __table_args__ = {"comment": "品牌信息表", "extend_existing": True}

    brand_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="品牌ID"
    )
    autohome_brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, unique=True, comment="汽车之家品牌ID"
    )
    brand_logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    brand_name_cn: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_country: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    brand_introduce: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
