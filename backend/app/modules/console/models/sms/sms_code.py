"""
短信验证码表
记录验证码发送与使用状态，用于验证码登录和验证码重置密码
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, SmallInteger, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class SmsCode(PlatformBase):
    """短信验证码"""
    __tablename__ = "sys_sms_code"
    __table_args__ = {"comment": "短信验证码表"}

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="手机号"
    )
    code: Mapped[str] = mapped_column(
        String(6), nullable=False, comment="验证码（6位数字）"
    )
    purpose: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="用途 1-验证码登录 2-重置密码 4-企业注册"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="状态 0-未使用 1-已使用 2-已过期"
    )
    expire_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="过期时间"
    )
    client_ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="请求IP"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
