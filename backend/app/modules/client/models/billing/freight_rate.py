"""
运价费率表（租户库）
"""

from typing import Optional
from datetime import date
from decimal import Decimal
from sqlalchemy import String, SmallInteger, BigInteger, Date, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FreightRate(TenantModelBase):
    """运价费率"""
    __tablename__ = "biz_freight_rate"
    __table_args__ = (
        Index(
            "idx_rate_match",
            "customer_id", "origin_code", "destination_code", "status", "is_deleted",
        ),
        {"comment": "运价费率表"},
    )
    __table_tier__ = "business"

    contract_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="合同ID"
    )
    customer_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="客户ID"
    )
    origin: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="出发地"
    )
    origin_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="出发地编码"
    )
    destination: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="目的地"
    )
    destination_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="目的地编码"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车辆品牌"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车型"
    )
    billing_mode: Mapped[int] = mapped_column(
        SmallInteger, default=0,
        comment="计费模式 0-台单价 1-单公里单价 2-整单价格"
    )
    distance_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True,
        comment="线路公里数（单公里计费时必填，客户标准）"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="单价"
    )
    price_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="运价类型 0-明确运价 1-预估运价"
    )
    effective_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="生效日期"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="到期日期"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-启用"
    )
