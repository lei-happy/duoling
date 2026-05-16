"""
运单货物明细表（租户库）
"""

from typing import Optional

from sqlalchemy import BigInteger, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class WaybillCargo(TenantModelBase):
    """运单货物明细（一单多品牌/车型）"""

    __tablename__ = "biz_waybill_cargo"
    __table_args__ = {"comment": "运单货物明细表"}
    __table_tier__ = "business"

    waybill_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="运单ID"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="排序序号"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="商品车品牌"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="商品车车型"
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准品牌ID（biz_vehicle_brand.brand_id）"
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准车系ID（biz_vehicle_series.series_id）"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="台数"
    )
    allocated_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="已分配到任务单的台数（应用层维护，约束 allocated<=quantity）"
    )
    cargo_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="明细版本号"
    )
