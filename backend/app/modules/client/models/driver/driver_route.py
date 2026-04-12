"""
驾驶员常跑线路表（租户库）

与 biz_driver 1:N 关联，一个司机可关联多条常跑线路。
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverRoute(TenantModelBase):
    """驾驶员常跑线路"""
    __tablename__ = "biz_driver_route"
    __table_args__ = {"comment": "驾驶员常跑线路表"}
    __table_tier__ = "business"

    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="关联驾驶员ID"
    )
    origin_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="出发地区域编码"
    )
    origin_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="出发地名称"
    )
    dest_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="目的地区域编码"
    )
    dest_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="目的地名称"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
