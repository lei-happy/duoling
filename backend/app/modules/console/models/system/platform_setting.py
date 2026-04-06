"""
平台键值配置表
"""

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class PlatformSetting(PlatformModelBase):
    """平台配置（如自助注册策略）"""

    __tablename__ = "sys_platform_setting"
    __table_args__ = {"comment": "平台配置表"}

    config_key: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="配置键（唯一）"
    )
    config_value: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="配置值"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="说明"
    )
