"""
平台用户表
存储平台管理员和各租户管理员的账号信息
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.base import PlatformModelBase


class User(PlatformModelBase):
    """平台用户"""
    __tablename__ = "sys_user"
    __table_args__ = {"comment": "平台用户表"}

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码（bcrypt哈希）"
    )
    real_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="真实姓名"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="手机号"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="邮箱"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="头像URL"
    )
    gender: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="性别 0-未知 1-男 2-女"
    )
    user_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="用户类型 0-平台管理员 1-租户管理员 2-租户用户 3-驾驶员"
    )
    tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, index=True, comment="所属租户编码（平台管理员为空）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    theme_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="用户主题配置（JSON格式）"
    )
