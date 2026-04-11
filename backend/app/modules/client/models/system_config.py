"""
系统配置表（租户库）
"""

from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SystemConfig(TenantModelBase):
    """系统配置"""
    __tablename__ = "biz_system_config"
    __table_args__ = {"comment": "系统配置表"}
    __table_tier__ = "core"

    config_key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="配置键"
    )
    config_value: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="配置值"
    )
    config_group: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="配置分组"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="描述"
    )
    value_type: Mapped[str] = mapped_column(
        String(20), default="string", server_default="string", comment="值类型"
    )
    default_value: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="默认值"
    )
