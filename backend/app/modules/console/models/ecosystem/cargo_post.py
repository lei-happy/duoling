"""服务平台货源挂牌扩展（平台库）

只放货源特有字段。线路、时间窗、数量、价格在 ``sys_eco_post`` 主表，
原因见 post.py 的模块注释。

安全约束：客户名称、货主单位、VIN 等敏感信息**绝对禁止**进入本表。
发布时在 Service 层就要过滤掉，不能依赖序列化层兜底。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, JSON, Numeric, SmallInteger, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoCargoPost(PlatformModelBase):
    """服务平台货源挂牌扩展"""

    __tablename__ = "sys_eco_cargo_post"
    __table_args__ = (
        UniqueConstraint("post_id", name="uk_eco_cargo_post"),
        {"comment": "服务平台货源挂牌扩展"},
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )

    # ===== 线路补充 =====
    via_points: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="途经点数组"
    )
    reference_mileage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 1), nullable=True, comment="参考里程（公里）"
    )
    segment_count: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="分段数量"
    )

    # ===== 货物 =====
    cargo_category: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="货物类别 1-商品车 2-普货 3-其他",
    )
    cargo_items: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True,
        comment="商品车明细 [{brand,series,quantity}]，不含 VIN",
    )
    vehicle_condition: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="车辆状态 1-新车 2-二手车 3-试驾车"
    )
    cargo_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="普货货物名称"
    )
    cargo_weight: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="普货重量（吨）"
    )
    cargo_volume: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="普货体积（立方）"
    )
    package_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="普货包装方式"
    )

    # ===== 承运要求 =====
    require_truck_types: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="需要车型编码数组"
    )
    require_slot_min: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="需要轿运车位数下限"
    )
    require_slot_max: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="需要轿运车位数上限"
    )
    allow_split: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否接受分批承运 0-否 1-是",
    )
    require_insurance: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否需要承运方投保 0-否 1-是",
    )
    other_requirements: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="其他要求（需过敏感内容拦截）"
    )

    # ===== 时间 =====
    arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="期望到达时间"
    )
    time_negotiable: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="时间是否可协商 0-否 1-是"
    )

    # ===== 结算 =====
    settle_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="结算方式 1-现结 2-月结 3-预付"
    )
    prepay_ratio: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="预付比例（%）"
    )

    # ===== 长期合作 =====
    freq_desc: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="预计货量频次，如「每周 3~5 车」"
    )
