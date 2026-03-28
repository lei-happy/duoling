"""
角色菜单关联表（租户库）
"""

from sqlalchemy import BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizRoleMenu(TenantModelBase):
    """角色菜单关联"""
    __tablename__ = "biz_role_menu"
    __table_args__ = (
        Index("idx_biz_rm_role_id", "role_id"),
        Index("idx_biz_rm_menu_id", "menu_id"),
        {"comment": "角色菜单关联表"},
    )

    role_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="角色ID"
    )
    menu_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="菜单ID"
    )
