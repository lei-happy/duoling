"""
产品功能清单与版本-功能关联表
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, BigInteger, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.base import PlatformModelBase


class ProductFeature(PlatformModelBase):
    """产品功能清单定义"""
    __tablename__ = "sys_product_feature"
    __table_args__ = {"comment": "产品功能清单表"}

    feature_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="功能编码"
    )
    feature_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="功能名称"
    )
    module: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="所属模块（base/resource/biz/finance/bi）"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="功能描述"
    )
    required_tables: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True,
        comment="该功能所需的租户库表名列表（JSON数组），版本开通时按需创建"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )


class VersionFeature(PlatformModelBase):
    """产品版本-功能关联"""
    __tablename__ = "sys_version_feature"
    __table_args__ = (
        Index("idx_vf_version_id", "version_id"),
        Index("idx_vf_feature_id", "feature_id"),
        {"comment": "版本功能关联表"},
    )

    version_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="产品版本ID"
    )
    feature_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="功能ID"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-启用"
    )
