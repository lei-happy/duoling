"""
承运价规则表（租户库）

与客户收入侧 biz_freight_rate 对称：承运商合同下的一条条承运价规则，
按「线路 + 车型 + 计费模式」维护给承运商的单价，供匹配引擎评分命中。
"""

from typing import Optional
from datetime import date
from decimal import Decimal
from sqlalchemy import String, SmallInteger, BigInteger, Integer, Date, Numeric, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CarrierRate(TenantModelBase):
    """承运价规则"""
    __tablename__ = "biz_carrier_rate"
    __table_args__ = (
        Index(
            "idx_crate_match",
            "carrier_id", "origin_code", "destination_code", "status", "is_deleted",
        ),
        Index(
            "idx_crate_match_region",
            "carrier_id", "origin_region_id", "destination_region_id", "status", "is_deleted",
        ),
        Index("idx_crate_contract", "contract_id"),
        {"comment": "承运价规则表"},
    )
    __table_tier__ = "business"

    contract_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="承运商合同ID"
    )
    carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="承运商ID"
    )
    origin: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="出发地"
    )
    origin_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="出发地编码"
    )
    origin_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="出发地行政区ID（biz_region.id）"
    )
    destination: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="目的地"
    )
    destination_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="目的地编码"
    )
    destination_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="目的地行政区ID（biz_region.id）"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车辆品牌"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车型"
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准品牌ID（biz_vehicle_brand.brand_id）"
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准车系ID（biz_vehicle_series.series_id）"
    )
    match_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="series", server_default=text("'series'"),
        comment="车型匹配类型 series/brand/general（与 brand_id/series_id 是否为空对齐）"
    )
    billing_mode: Mapped[int] = mapped_column(
        SmallInteger, default=0,
        comment="计费模式 0-台单价 1-单公里单价 2-整单价格"
    )
    distance_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True,
        comment="线路公里数（单公里计费时必填）"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="单价"
    )
    min_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="最低运费（命中后兜底）"
    )
    price_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="运价类型 0-明确运价 1-预估运价"
    )
    is_bidirectional: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="是否双向 0-否 1-是"
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="人工优先级（数值越大越优先）"
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
    rule_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="规则版本号（每次更新+1，旧版本快照在 biz_carrier_rate_change_log）"
    )
