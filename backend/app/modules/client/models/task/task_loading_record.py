"""
任务单装卸记录表（租户库）

支持任务单多批次装/卸车：例如 8 台车在 A 地装 4 台、B 地装 4 台，
每次装/卸车产出一条装卸记录（含照片、地点、操作人、关联调令、关联 item）。

设计要点：
- 一次装卸事件 = 一条 ``biz_task_loading_record`` + N 条 ``biz_task_loading_record_item``
- ``event_type`` 区分装车 / 卸车；签收事件单独由 ``TaskWaybillItem.signed_at`` 承载
- ``item.status`` 由记录创建/撤销驱动（Service 层在事务内同步推进）
- ``photo_urls`` 用 JSON 列存储 OSS URL 数组（前端最多上传 9 张）
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON, BigInteger, DateTime, Index, Integer, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskLoadingRecord(TenantModelBase):
    """任务单装卸事件主表"""

    __tablename__ = "biz_task_loading_record"
    __table_args__ = (
        Index("idx_loading_record_task_id", "task_id"),
        Index("idx_loading_record_dispatch_order_id", "dispatch_order_id"),
        Index("idx_loading_record_event_type", "event_type"),
        Index("idx_loading_record_happened_at", "happened_at"),
        {"comment": "任务单装卸事件记录表（多批次装/卸车主表）"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    dispatch_order_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="关联 biz_task_dispatch_order.id（多调令任务必填）",
    )
    event_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="事件类型 1-装车 2-卸车",
    )
    happened_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="实际装/卸时间"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="装/卸地点名称"
    )
    location_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="地点行政区编码"
    )
    location_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="地点行政区 ID"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="本次装/卸总台数（冗余 = SUM(record_item.quantity)）",
    )
    photo_urls: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True,
        comment="照片 URL 数组（OSS 路径，最多 9 张）",
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )


class TaskLoadingRecordItem(TenantModelBase):
    """装卸事件 ↔ 任务挂接行 桥接表"""

    __tablename__ = "biz_task_loading_record_item"
    __table_args__ = (
        Index("idx_loading_record_item_record_id", "record_id"),
        Index("idx_loading_record_item_item_id", "item_id"),
        {"comment": "装卸记录与挂接货物的桥接表"},
    )
    __table_tier__ = "business"

    record_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task_loading_record.id"
    )
    item_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task_waybill_item.id"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="本次该 item 装/卸的台数（>0，允许 < item.quantity 远期支持 item 内拆批）",
    )
