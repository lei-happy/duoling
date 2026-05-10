"""
挂车核心表（租户库）

仅保留业务必须字段，详细属性存储在扩展表 biz_trailer_ext 中。
"""

from sqlalchemy import String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Trailer(TenantModelBase):
    """挂车核心信息"""
    __tablename__ = "biz_trailer"
    __table_args__ = {"comment": "挂车核心表"}
    __table_tier__ = "business"

    plate_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="挂车车牌号"
    )
    plate_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="YELLOW",
        comment="车牌类型 BLUE/YELLOW/NEW_ENERGY",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
