"""
智能配载 - 方案表（biz_smart_stowage_plan）

一条生成任务可产出多个候选配载方案。每个方案对应「一组商品车 = 一个配载单」
的推荐，调度员采纳后经 TaskService.create_task 落为 biz_task(source=2)。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


# 方案状态
PLAN_STATUS_PENDING = 0   # 待采纳
PLAN_STATUS_ADOPTED = 1   # 已采纳
PLAN_STATUS_IGNORED = 2   # 已忽略


class SmartStowagePlan(TenantModelBase):
    """智能配载推荐方案"""

    __tablename__ = "biz_smart_stowage_plan"
    __table_args__ = (
        Index("idx_ssp_plan_task", "plan_task_id"),
        Index("idx_ssp_status", "status"),
        {"comment": "智能配载推荐方案表"},
    )
    __table_tier__ = "business"

    plan_task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联生成任务ID(biz_smart_stowage_task)"
    )
    plan_no: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="方案序号(同一生成任务内 1,2,3...)",
    )

    origin: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="方案主线路-起"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="方案主线路-终"
    )

    vehicle_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="商品车台数",
    )
    occupied_spots: Mapped[float] = mapped_column(
        Numeric(6, 2), nullable=False, default=0, server_default=text("0"),
        comment="折算占用车位",
    )
    target_spots: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="目标板车车位数",
    )
    load_rate: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=0, server_default=text("0"),
        comment="装载率(0-100)",
    )

    customer_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="涉及客户数",
    )
    waybill_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="涉及运单数",
    )

    score: Mapped[float] = mapped_column(
        Numeric(8, 4), nullable=False, default=0, server_default=text("0"),
        comment="综合评分(越大越优)",
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="可解释理由"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=PLAN_STATUS_PENDING,
        server_default=text("0"),
        comment="状态 0待采纳 1已采纳 2已忽略",
    )
    adopted_task_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="采纳后生成的任务单ID(biz_task)"
    )
    adopted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="采纳时间"
    )
