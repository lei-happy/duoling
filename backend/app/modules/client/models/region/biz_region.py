"""
地区表（租户库）
注册时从平台 sys_regions 同步（source=0），企业可自行添加自定义地区（source=1）
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy import String, SmallInteger, Integer, BigInteger, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizRegion(TenantModelBase):
    """行政区域"""
    __tablename__ = "biz_region"
    __table_args__ = (
        Index("idx_biz_region_parent_code", "parent_code"),
        Index("idx_biz_region_level", "level"),
        Index("idx_biz_region_source", "source"),
        {"comment": "行政区域表"},
    )

    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="行政区划代码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="名称"
    )
    parent_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="上级行政区划代码"
    )
    level: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="层级 1-省 2-市 3-区/县 4-自定义子级"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    source: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="数据来源 0-系统初始化 1-企业自定义"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, default=None, comment="创建人用户ID"
    )
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True, default=None, comment="经度（东经为正）"
    )
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6), nullable=True, default=None, comment="纬度（北纬为正）"
    )
