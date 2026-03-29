"""
用户企业关联表
同一用户可关联多个企业，每个企业中有独立的角色类型和状态
"""

from sqlalchemy import BigInteger, String, SmallInteger, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class UserTenant(PlatformModelBase):
    """用户-企业关联"""
    __tablename__ = "sys_user_tenant"
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_code", name="uk_user_tenant"),
        Index("idx_tenant_code", "tenant_code"),
        Index("idx_user_id", "user_id"),
        {"comment": "用户企业关联表"},
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="用户ID"
    )
    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="企业编码"
    )
    user_type: Mapped[int] = mapped_column(
        SmallInteger, default=2, comment="角色类型 1-租户管理员 2-租户用户 3-驾驶员"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
