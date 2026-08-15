"""能源供应商（租户库）"""

from typing import Optional

from sqlalchemy import Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergySupplier(TenantModelBase):
    """能源供应商"""

    __tablename__ = "biz_energy_supplier"
    __table_args__ = (
        Index("uk_energy_supplier_code", "supplier_code", unique=True),
        {"comment": "能源供应商表"},
    )
    __table_tier__ = "business"

    supplier_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="供应商编码（租户内唯一）"
    )
    supplier_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="供应商名称"
    )
    supplier_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=9, server_default=text("9"),
        comment="类型 1-石油石化 2-燃气 3-充电 4-能源平台 5-民营油站 9-其他",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常",
    )
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="联系电话"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
