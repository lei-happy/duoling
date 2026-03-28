"""
企业角色表（租户库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizRole(TenantModelBase):
    """企业角色"""
    __tablename__ = "biz_role"
    __table_args__ = {"comment": "企业角色表"}

    role_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="角色编码"
    )
    role_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="角色名称"
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
