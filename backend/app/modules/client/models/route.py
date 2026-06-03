"""
路线管理表（租户库）
"""

from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Route(TenantModelBase):
    """路线"""
    __tablename__ = "biz_route"
    __table_args__ = (
        Index(
            "idx_biz_route_region_pair",
            "is_deleted",
            "origin_region_id",
            "destination_region_id",
        ),
        {"comment": "路线表"},
    )
    __table_tier__ = "business"

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
    origin_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="出发地行政区ID（biz_region.id）"
    )
    destination_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="目的地行政区ID（biz_region.id）"
    )
    origin_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="出发地国标区划码"
    )
    destination_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="目的地国标区划码"
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
    route_polyline: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="驾车路线折线 JSON：[[lng,lat],...]，供地图预览"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
