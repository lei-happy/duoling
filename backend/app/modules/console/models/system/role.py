"""
角色表
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class Role(PlatformModelBase):
    """角色"""
    __tablename__ = "sys_role"
    __table_args__ = {"comment": "角色表"}

    role_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="角色编码"
    )
    role_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="角色名称"
    )
    role_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="角色类型 0-平台角色 1-租户角色"
    )
    tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, index=True, comment="所属租户编码（平台角色为空）"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
