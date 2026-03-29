"""
菜单/权限项表
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class Menu(PlatformModelBase):
    """菜单"""
    __tablename__ = "sys_menu"
    __table_args__ = {"comment": "菜单表"}

    parent_id: Mapped[int] = mapped_column(
        BigInteger, default=0, comment="父级菜单ID（0为顶级）"
    )
    menu_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="菜单名称"
    )
    menu_code: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="权限标识"
    )
    menu_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="类型 0-目录 1-菜单 2-按钮"
    )
    path: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="路由路径"
    )
    component: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="组件路径"
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="图标"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    visible: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="是否可见 0-隐藏 1-显示"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    app_type: Mapped[str] = mapped_column(
        String(20), default="platform", comment="归属应用 platform/console/client"
    )
    feature_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True,
        comment="关联功能编码，用于产品版本控制菜单可见性"
    )
