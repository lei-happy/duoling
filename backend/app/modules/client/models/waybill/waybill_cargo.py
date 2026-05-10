"""
运单货物明细表（租户库）
"""

from typing import Optional

from sqlalchemy import BigInteger, Integer, String
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
    quantity: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="台数"
    )
