"""
智能配载 - 方案明细表（biz_smart_stowage_plan_item）

方案内的商品车挂接明细，三要素 (waybill_id, waybill_cargo_id, quantity)
可直接映射为 TaskWaybillItemIn，用于采纳时构造 TaskCreate。
"""

from typing import Optional

from sqlalchemy import (
    BigInteger,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SmartStowagePlanItem(TenantModelBase):
    """智能配载方案明细（商品车挂接候选）"""

    __tablename__ = "biz_smart_stowage_plan_item"
    __table_args__ = (
        Index("idx_sspi_plan", "plan_id"),
        {"comment": "智能配载方案明细表"},
    )
    __table_tier__ = "business"

    plan_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联方案ID(biz_smart_stowage_plan)"
    )

    waybill_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="运单ID"
    )
    waybill_cargo_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="运单货物明细ID(商品车)"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="配载台数",
    )

    # ---- 展示快照 ----
    waybill_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="运单号"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="客户ID"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="客户名称"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="品牌"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="车型"
    )
    vin: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="车架号"
    )
    origin: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="起"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="终"
    )
    occupy_coefficient: Mapped[float] = mapped_column(
        Numeric(4, 2), nullable=False, default=1, server_default=text("1"),
        comment="该行占位系数",
    )
