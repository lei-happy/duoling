"""服务平台运力挂牌扩展（平台库）

只放运力特有字段。线路、时间窗、数量、价格在 ``sys_eco_post`` 主表。

个人敏感信息的处理约定（见 08.接口契约.md §2.4）：
  - ``driver_name`` 存原值但**永不出现在任何对外接口的响应中**，只用于
    成交后由承运方主动提供、以及运营核查。对外只给 ``driver_display``。
  - **司机手机号不落本表**。需要时回源租户库读取；成交后写入
    ``sys_eco_deal.driver_phone``，且仅对成交双方可见。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, Numeric, SmallInteger, String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoCapacityPost(PlatformModelBase):
    """服务平台运力挂牌扩展"""

    __tablename__ = "sys_eco_capacity_post"
    __table_args__ = (
        UniqueConstraint("post_id", name="uk_eco_capacity_post"),
        Index("idx_eco_capacity_slot", "truck_type", "slot_count"),
        {"comment": "服务平台运力挂牌扩展"},
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )
    post_granularity: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="挂牌粒度 1-指定车辆 2-车队打包",
    )

    # ===== 车辆 =====
    truck_type: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="车辆类型"
    )
    slot_count: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="轿运车位数"
    )
    truck_length: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="车长（米）"
    )
    rated_load: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="核定载重（吨）"
    )
    truck_quantity: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1",
        comment="车辆数量，指定车辆时为 1",
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号（原值，按层级脱敏后对外）"
    )
    plate_masked: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号（打码值，认证层展示）"
    )
    plate_public: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否完全公开车牌 0-否 1-是",
    )
    has_trailer: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否带挂 0-否 1-是"
    )
    trailer_plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="挂车车牌"
    )

    # ===== 司机（driver_name 永不对外返回；手机号不落库）=====
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="司机姓名（原值，永不对外返回）"
    )
    driver_display: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="司机对外展示串，如「王师傅」"
    )
    driver_years: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="驾龄（年）"
    )
    driver_order_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="司机历史完成单数（统计快照）"
    )

    # ===== 位置与档期 =====
    departure_ready_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="可出发时间（车在途时填预计到达当前地时间）",
    )
    pickup_radius: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="可接受取货半径（公里）"
    )

    # ===== 运营能力 =====
    good_at_categories: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="擅长货物类别数组"
    )
    can_invoice: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否可开票 0-否 1-是"
    )
    invoice_type: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="票种"
    )
    has_insurance: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否有承运保险 0-否 1-是",
    )
    service_promise: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="服务承诺（需过敏感内容拦截）"
    )

    # ===== 结算 =====
    settle_require: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="结算要求 1-现结 2-月结可接受 3-需预付",
    )
