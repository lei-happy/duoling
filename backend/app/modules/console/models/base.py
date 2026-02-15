"""
平台模型基类
提供通用字段（id, created_at, updated_at, is_deleted）
"""

from datetime import datetime
from sqlalchemy import BigInteger, DateTime, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class PlatformModelBase(PlatformBase):
    """平台库模型基类"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否删除 0-否 1-是"
    )
