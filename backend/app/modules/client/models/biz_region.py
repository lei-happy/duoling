"""
地区表（租户库）
注册时从平台 sys_regions 同步
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizRegion(TenantModelBase):
    """全国行政区划"""
    __tablename__ = "biz_region"
    __table_args__ = (
        Index("idx_biz_region_parent_code", "parent_code"),
        Index("idx_biz_region_level", "level"),
        {"comment": "全国行政区域表"},
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
        SmallInteger, default=1, comment="层级 1-省 2-市 3-区/县"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
