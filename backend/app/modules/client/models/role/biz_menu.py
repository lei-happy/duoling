"""
企业菜单表（租户库）
记录企业自定义的菜单权限配置
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizMenu(TenantModelBase):
    """企业菜单"""
    __tablename__ = "biz_menu"
    __table_args__ = {"comment": "企业菜单表"}

    parent_id: Mapped[int] = mapped_column(
        BigInteger, default=0, comment="父级菜单ID"
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
