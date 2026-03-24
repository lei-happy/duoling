"""
用户角色关联表（租户库）
"""

from sqlalchemy import BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizUserRole(TenantModelBase):
    """用户角色关联"""
    __tablename__ = "biz_user_role"
    __table_args__ = (
        Index("idx_biz_ur_user_id", "user_id"),
        Index("idx_biz_ur_role_id", "role_id"),
        {"comment": "用户角色关联表"},
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="用户ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="角色ID"
    )
