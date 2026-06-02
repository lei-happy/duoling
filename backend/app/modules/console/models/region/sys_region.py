"""
平台地区表（平台库 sys_regions）
全国行政区划主数据，新租户注册时同步至租户库 biz_region
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime

from sqlalchemy import (
    BigInteger, String, SmallInteger, Integer, DateTime, Index, Numeric, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class SysRegion(PlatformBase):
    """全国行政区域"""
    __tablename__ = "sys_regions"
    __table_args__ = (
        Index("name", "name"),
        Index("level", "level"),
        Index("pcode", "pcode"),
        {"comment": "全国行政区域表", "extend_existing": True},
    )

    code: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False, comment="区划代码"
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, default="", comment="名称"
    )
    short_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, default=None, comment="简称"
    )
    level: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="层级 1省 2市 3区县 4街道"
    )
    pcode: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, default=None, comment="父级区划代码"
    )
    citycode: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, default=None, comment="高德 citycode"
    )
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True, default=None, comment="经度（东经为正）"
    )
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True, default=None, comment="纬度（北纬为正）"
    )
    category: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, comment="城乡分类"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="状态 0-停用 1-正常"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否删除 0-否 1-是"
    )
