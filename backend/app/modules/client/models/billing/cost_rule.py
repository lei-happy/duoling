"""
成本费用规则表（租户库）

定义"某费用类型在某适用范围下如何计价"，类比收入侧运价明细 biz_freight_rate，
但多了 fee_type / pricing_method / 收款方 / 阶梯 / 比例等支出侧特有字段。
"""

from typing import Optional
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    String, SmallInteger, BigInteger, Integer, Date, Numeric, JSON, Index, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CostRule(TenantModelBase):
    """成本费用规则"""

    __tablename__ = "biz_cost_rule"
    __table_args__ = (
        Index("idx_cost_rule_policy", "policy_id"),
        Index("idx_cost_rule_fee_type", "fee_type", "status", "is_deleted"),
        Index("idx_cost_rule_route", "origin_region_id", "destination_region_id"),
        Index("idx_cost_rule_series", "series_id"),
        Index("idx_cost_rule_brand", "brand_id"),
        {"comment": "成本费用规则表"},
    )
    __table_tier__ = "business"

    policy_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="所属成本政策ID"
    )

    fee_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="费用类型（字典 cost_fee_type）：driver_freight/car_wash/loading/...",
    )
    fee_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="费用名称（字典 label 冗余）"
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="方向 1-应付加项 2-扣减项",
    )

    pricing_method: Mapped[str] = mapped_column(
        String(32), nullable=False, default="per_vehicle",
        server_default=text("'per_vehicle'"),
        comment="计价方式 per_vehicle/per_km/per_trip/per_ton_km/fixed/percentage/tiered",
    )
    qty_dimension: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="计价数量维度 vehicle/km/trip/ton"
    )
    multiply_by_qty: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="每公里/每吨公里是否再乘台数 0-否 1-是",
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"),
        comment="单价（含义随 pricing_method 变化）",
    )
    distance_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True,
        comment="政策核定里程（per_km 时优先于线路里程）",
    )
    min_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="该费用项保底金额"
    )
    max_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="该费用项封顶金额"
    )
    round_mode: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="取整方式 0-不取整 1-四舍五入到元 2-进一法到元",
    )

    # 阶梯计价（pricing_method=tiered）：[{"upTo": 100, "unitPrice": 5.0}, ...]
    tiers_json: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="阶梯分段配置（tiered 计价时使用）"
    )
    # 按比例计价（pricing_method=percentage）
    percent_base: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True,
        comment="比例计价基数来源 freight_income/fixed_base（percentage 计价时使用）",
    )
    rate_percent: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4), nullable=True, comment="比例（%，percentage 计价时使用）"
    )

    payee_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="收款方类型 1-司机 2-承运商 3-社会运力",
    )

    # 适用范围：线路（复用收入侧行政区层级向上兼容匹配）
    origin_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="出发地行政区ID（biz_region.id），空表示不限线路",
    )
    origin_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="出发地编码"
    )
    origin: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="出发地名称"
    )
    destination_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="目的地行政区ID"
    )
    destination_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="目的地编码"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="目的地名称"
    )
    is_bidirectional: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="线路是否双向 0-否 1-是",
    )

    # 适用范围：车型（复用收入侧品牌/车系层级）
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准品牌ID，空表示不限品牌"
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="标准车系ID，空表示不限车型"
    )

    # 条件引擎 v2：AND/OR 条件树（JSON）。为空时由 legacy 列合成等价条件树，
    # 保证存量规则零迁移向后兼容。结构见 conditions 包 base.py。
    conditions_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True,
        comment="AND/OR 条件树（可插拔条件类型），空则回退 legacy 列(线路/车型)",
    )

    effective_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="规则生效日期（空则继承政策）"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="规则失效日期（空则继承政策）"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-启用",
    )
    price_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="价格类型 0-明确 1-预估",
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="人工优先级（越大越优先）",
    )
    rule_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="规则版本号（每次更新+1，旧版本快照在 biz_cost_rule_change_log）",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="更新人"
    )

    def condition_tree(self) -> dict:
        """返回本规则的 AND/OR 条件树。

        - conditions_json 非空：直接使用（v2 规则）。
        - 否则由 legacy 列合成等价 AND 树（线路 region_route + 车型 vehicle_*），
          使存量规则在新引擎下的命中与评分与旧引擎完全一致（零数据迁移）。
        """
        cj = self.conditions_json
        if cj:
            return cj

        children: list[dict] = []
        if self.origin_region_id is not None or self.destination_region_id is not None:
            children.append({
                "type": "region_route",
                "originRegionId": self.origin_region_id,
                "destinationRegionId": self.destination_region_id,
                "bidirectional": self.is_bidirectional or 0,
            })
        if self.series_id is not None:
            children.append({
                "type": "vehicle_series", "op": "eq", "value": self.series_id,
            })
        elif self.brand_id is not None:
            children.append({
                "type": "vehicle_brand", "op": "eq", "value": self.brand_id,
            })
        return {"logic": "and", "children": children}
