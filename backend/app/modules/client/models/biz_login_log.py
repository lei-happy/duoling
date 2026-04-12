"""
登录日志表（租户库）
"""

from typing import Optional

from sqlalchemy import String, SmallInteger, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizLoginLog(TenantModelBase):
    """租户级登录日志"""
    __tablename__ = "biz_login_log"
    __table_args__ = {"comment": "登录日志表"}

    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="租户内 biz_user.id"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="登录账号（一般为手机号）"
    )
    os: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="操作系统"
    )
    device: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="设备型号"
    )
    browser: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="浏览器/UA"
    )
    ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="IP地址"
    )
    login_type: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        comment="0登录成功 1登录失败 2退出登录 3续签token",
    )
    comments: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
