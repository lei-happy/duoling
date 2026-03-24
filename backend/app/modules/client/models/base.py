"""
租户业务库模型基类

通过 __table_tier__ 属性实现渐进式表初始化：
  - "core"     : 注册即创建（基础设施层）
  - "business" : 业务模块开发后、版本开通时创建（业务表）
  - "premium"  : 高级版本开通时创建（版本功能表）
"""

from datetime import datetime
from sqlalchemy import BigInteger, DateTime, SmallInteger, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TenantBase


class TenantModelBase(TenantBase):
    """租户库模型基类"""
    __abstract__ = True
    __table_tier__ = "core"

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
        SmallInteger, default=0, server_default=text("0"), comment="是否删除 0-否 1-是"
    )
