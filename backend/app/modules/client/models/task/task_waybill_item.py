"""
任务单-运单货物挂接表（租户库）

最小单位 = (waybill_cargo_id, 分配台数)。一张运单的同一 cargo 行可被多个任务单分配，
通过应用层原子校验 cargo.quantity >= SUM(item.quantity WHERE waybill_cargo_id=X AND status<3)。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskWaybillItem(TenantModelBase):
    """任务单货物挂接（按 cargo 行 + 台数）"""

    __tablename__ = "biz_task_waybill_item"
    __table_args__ = (
        Index("idx_twi_task_id", "task_id"),
        Index("idx_twi_waybill_id", "waybill_id"),
        Index("idx_twi_cargo_id", "waybill_cargo_id"),
        Index("idx_twi_status", "status"),
        {"comment": "任务单-运单货物挂接表"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    waybill_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_waybill.id"
    )
    waybill_cargo_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_waybill_cargo.id（最小单位）"
    )

    # ===== 冗余快照 =====
    waybill_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="运单号（冗余）"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="客户 ID（冗余）"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称（冗余）"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="商品车品牌（冗余）"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="商品车型号（冗余）"
    )
    dealer_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="收车门店（冗余）"
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="本任务分到的台数（>0）"
    )
    segment_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="可选指定走某段（NULL=跟随主任务）"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-待装车 1-已装车 2-已卸车 3-已签收",
    )
    loaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="装车时间"
    )
    unloaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="卸车时间"
    )
    signed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="签收时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
