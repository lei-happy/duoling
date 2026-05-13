"""
车型/品牌别名表（租户库）
将运单/导入数据里的非标准品牌+车型映射到标准 brand_id / series_id
"""

from typing import Optional

from sqlalchemy import (
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class VehicleAlias(TenantModelBase):
    """车型/品牌别名

    alias_kind:
      - brand : alias_name 仅匹配品牌（series_id 为空）
      - series: alias_name 匹配 (品牌+车型) 组合（brand_id+series_id 同时给出）
    """

    __tablename__ = "biz_vehicle_alias"
    __table_args__ = (
        UniqueConstraint("alias_name", name="uk_vehicle_alias_name"),
        Index("idx_vehicle_alias_brand", "brand_id"),
        Index("idx_vehicle_alias_series", "series_id"),
        {"comment": "车型/品牌别名表"},
    )
    __table_tier__ = "business"

    alias_name: Mapped[str] = mapped_column(
        String(200), nullable=False,
        comment="别名（品牌别名 = 品牌串；车系别名 = '品牌\\x1f车型' 串，与运单内部 key 对齐）"
    )
    alias_kind: Mapped[str] = mapped_column(
        String(16), nullable=False, default="series",
        server_default=text("'series'"),
        comment="别名类型 brand/series"
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准品牌ID"
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准车系ID"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-启用"
    )
