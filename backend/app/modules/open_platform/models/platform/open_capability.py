"""开放平台 - 能力目录（平台库）

事实源在代码 @register_capability，本表为同步产物，供控制面展示与文档生成。
"""

from typing import Optional

from sqlalchemy import String, SmallInteger, Integer, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class OpenCapability(PlatformBase):
    """能力目录（code 作主键，与代码注册表一致）"""

    __tablename__ = "open_capability"
    __table_args__ = (
        Index("ix_open_cap_category", "category"),
        Index("ix_open_cap_status", "status"),
        {"comment": "开放平台能力目录"},
    )

    code: Mapped[str] = mapped_column(
        String(64), primary_key=True, comment="能力码，如 waybill.query"
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="业务名称")
    category: Mapped[str] = mapped_column(
        String(32), nullable=False, default="", server_default="", comment="分类"
    )
    description: Mapped[str] = mapped_column(
        String(512), nullable=False, default="", server_default="", comment="说明"
    )
    channels: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="支持通道 ['api','mcp']"
    )
    read_only: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否只读 1-是 0-否"
    )
    input_schema: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="入参 JSON Schema"
    )
    output_fields: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="对外可见字段白名单"
    )
    sensitive_fields: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="脱敏字段"
    )
    risk_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="low", server_default="low", comment="low / high"
    )
    stability: Mapped[str] = mapped_column(
        String(16), nullable=False, default="stable", server_default="stable",
        comment="beta / stable / deprecated / offline",
    )
    version: Mapped[str] = mapped_column(
        String(8), nullable=False, default="v1", server_default="v1", comment="契约版本"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="enabled", server_default="enabled",
        comment="enabled / disabled",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="展示排序"
    )
