"""
跨租户承运商互联关系镜像（平台库）
B 端反查"哪些 A 把我加为承运商"的加速表，由 A 端 biz_carrier.linked_tenant_code
状态变化时同步刷新
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, Date, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class CarrierLink(PlatformModelBase):
    """承运商互联关系镜像"""
    __tablename__ = "sys_carrier_link"
    __table_args__ = (
        UniqueConstraint("source_tenant_code", "source_carrier_id", name="uk_source"),
        Index("idx_linked", "linked_tenant_code", "link_status"),
        {"comment": "跨租户承运商互联关系（B 端反查加速）"},
    )

    source_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="A 的 tenant_code"
    )
    source_carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="A.biz_carrier.id"
    )
    source_carrier_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="A 中维护的承运商名（脱敏冗余）"
    )
    source_tenant_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="A 的企业名（脱敏冗余）"
    )
    linked_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="B 的 tenant_code"
    )
    link_status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="1-激活 2-A 端已删除 3-B 端已退出",
    )
    cooperation_start: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="合作起始日"
    )
