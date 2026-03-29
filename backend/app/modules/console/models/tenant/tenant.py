"""
租户/企业信息表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, SmallInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class Tenant(PlatformModelBase):
    """租户/企业信息"""
    __tablename__ = "sys_tenant"
    __table_args__ = {"comment": "租户/企业信息表"}

    tenant_code: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="租户编码（唯一标识）"
    )
    tenant_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="企业名称"
    )
    short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="企业简称"
    )
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联系电话"
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="联系邮箱"
    )
    province: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="省份"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="城市"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="详细地址"
    )
    logo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="企业Logo URL"
    )
    license_no: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="营业执照号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常 3-已过期"
    )
    db_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="租户数据库名称"
    )
    db_initialized: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="数据库是否已初始化 0-否 1-是"
    )
    expire_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="授权到期时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    source_channel: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="来源渠道: website-官网注册 console-后台录入 referral-企业推荐"
    )
    referrer_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="推荐人企业编码（来源为referral时记录）"
    )
    in_follow_pool: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="是否在跟进池 0-否 1-是"
    )
    follow_remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="跟进备注"
    )
