"""
客户管理表（租户库）
企业的客户（托运方/收货方）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Customer(TenantModelBase):
    """客户"""
    __tablename__ = "biz_customer"
    __table_args__ = {"comment": "客户表"}

    customer_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="客户名称"
    )
    short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="客户简称"
    )
    customer_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="客户类型 0-托运方 1-收货方 2-两者兼具"
    )
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联系电话"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="地址"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
