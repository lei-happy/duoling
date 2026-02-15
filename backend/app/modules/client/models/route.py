"""
路线管理表（租户库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Route(TenantModelBase):
    """路线"""
    __tablename__ = "biz_route"
    __table_args__ = {"comment": "路线表"}

    route_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="路线名称"
    )
    route_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True, comment="路线编码"
    )
    origin: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="起点"
    )
    destination: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="终点"
    )
    distance: Mapped[Optional[str]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="距离（公里）"
    )
    estimated_hours: Mapped[Optional[str]] = mapped_column(
        Numeric(5, 1), nullable=True, comment="预计耗时（小时）"
    )
    waypoints: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="途经点（JSON数组）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
