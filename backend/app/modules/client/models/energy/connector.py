"""能源连接器实例配置（租户库）"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, BigInteger, DateTime, Index, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyConnector(TenantModelBase):
    """能源连接器实例"""

    __tablename__ = "biz_energy_connector"
    __table_args__ = (
        Index("idx_energy_connector_supplier", "supplier_id"),
        {"comment": "能源连接器实例配置"},
    )
    __table_tier__ = "business"

    connector_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="连接器类型编码 excel/manual/http_api"
    )
    connector_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="实例名称"
    )
    supplier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="供应商 ID"
    )
    account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="默认能源账户 ID"
    )
    auth_config_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="鉴权配置（加密存储，一期明文 JSON）"
    )
    field_mapping_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="字段映射：外部字段 → 内部标准字段"
    )
    sync_mode: Mapped[str] = mapped_column(
        String(16), nullable=False, default="manual",
        server_default=text("'manual'"),
        comment="同步模式 realtime/interval/cron/manual",
    )
    cron: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="cron 表达式"
    )
    last_success_cursor: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="断点续传游标"
    )
    last_sync_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近成功同步时间"
    )
    last_error: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="最近一次错误"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
