"""
AI 模块内部基类（避免与 client / console models __init__ 形成循环导入）

- AiPlatformBase : 平台库 AI 元数据基类（id / created_at / updated_at / is_deleted）
- AiTenantBase   : 租户库 AI 业务基类（同上 + __table_tier__）
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase, TenantBase


class AiPlatformBase(PlatformBase):
    """AI 模块平台库基类"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否删除 0-否 1-是"
    )


class AiTenantBase(TenantBase):
    """AI 模块租户库基类（默认 business 层级，按需开通）"""

    __abstract__ = True
    __table_tier__ = "business"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default=text("0"), comment="是否删除 0-否 1-是"
    )
