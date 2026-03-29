"""
用户-角色关联表
"""

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class UserRole(PlatformModelBase):
    """用户-角色关联"""
    __tablename__ = "sys_user_role"
    __table_args__ = {"comment": "用户角色关联表"}

    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="用户ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="角色ID"
    )
