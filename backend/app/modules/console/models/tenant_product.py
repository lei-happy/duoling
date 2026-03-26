"""
租户-产品版本授权关系表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, BigInteger, DateTime, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.base import PlatformModelBase


class TenantProduct(PlatformModelBase):
    """租户产品授权"""
    __tablename__ = "sys_tenant_product"
    __table_args__ = {"comment": "租户产品版本授权表"}

    tenant_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="租户ID"
    )
    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True, comment="租户编码"
    )
    version_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="产品版本ID"
    )
    version_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="产品版本编码"
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="授权开始时间"
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="授权到期时间"
    )
    grant_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="开通类型(数据字典 grant_type)"
    )
    grant_remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="开通备注"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
