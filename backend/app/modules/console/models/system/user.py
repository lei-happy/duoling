"""
平台用户表
存储所有用户的账号信息（用户唯一性由 phone 保证）
用户与企业的关联通过 sys_user_tenant 表实现
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class User(PlatformModelBase):
    """平台用户"""
    __tablename__ = "sys_user"
    __table_args__ = {"comment": "平台用户表"}

    phone: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="手机号（登录标识，全平台唯一）"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码（bcrypt哈希）"
    )
    real_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="真实姓名"
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
        SmallInteger, default=2,
        comment="用户类型 0-平台管理员（其余值仅做默认标记，实际角色由 sys_user_tenant 决定）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    force_change_pwd: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="是否强制修改密码 0-否 1-是"
    )
    theme_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="用户主题配置（JSON格式）"
    )
    workplace_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="工作台个性化配置（JSON格式）"
    )
