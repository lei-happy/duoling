"""
产品版本管理表
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.base import PlatformModelBase


class ProductVersion(PlatformModelBase):
    """产品版本"""
    __tablename__ = "sys_product_version"
    __table_args__ = {"comment": "产品版本表"}

    version_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="版本编码（如 basic/standard/pro/enterprise）"
    )
    version_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="版本名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="版本说明"
    )
    features: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="功能清单（JSON格式，菜单编码列表等）"
    )
    max_users: Mapped[int] = mapped_column(
        default=10, comment="最大用户数"
    )
    max_vehicles: Mapped[int] = mapped_column(
        default=50, comment="最大车辆数"
    )
    price: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="价格"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
