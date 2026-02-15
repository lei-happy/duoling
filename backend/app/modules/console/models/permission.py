"""
角色-菜单关联表
"""

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.base import PlatformModelBase


class RoleMenu(PlatformModelBase):
    """角色-菜单关联"""
    __tablename__ = "sys_role_menu"
    __table_args__ = {"comment": "角色菜单关联表"}

    role_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="角色ID"
    )
    menu_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="菜单ID"
    )
