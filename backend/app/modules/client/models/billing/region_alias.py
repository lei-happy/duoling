"""
地名别名表（租户库）
将运单/导入数据里的非标准地名映射到 biz_region.id
"""

from sqlalchemy import (
    BigInteger,
    Index,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class RegionAlias(TenantModelBase):
    """地名别名"""

    __tablename__ = "biz_region_alias"
    __table_args__ = (
        UniqueConstraint("alias_name", name="uk_region_alias_name"),
        Index("idx_region_alias_region", "region_id"),
        {"comment": "地名别名表"},
    )
    __table_tier__ = "business"

    alias_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="别名（标准化前的字符串，去空白）"
    )
    region_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="目标行政区ID（biz_region.id）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-启用"
    )
