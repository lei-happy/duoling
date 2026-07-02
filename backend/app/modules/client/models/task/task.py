"""
运输任务单主表（租户库）

任务单表达"由谁运输哪些货物走哪条线"，是物流公司调度环节的核心单据。
与运单的关系：M:N 按台数拆分，挂接在 biz_task_waybill_item。
与财务：解耦设计，1 个任务单可挂多张 biz_task_finance_doc。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Task(TenantModelBase):
    """运输任务单主表"""

    __tablename__ = "biz_task"
    __table_args__ = (
        Index("idx_task_status", "status"),
        Index("idx_task_carrier_type", "carrier_type"),
        Index("idx_task_capacity_id", "capacity_id"),
        Index("idx_task_carrier_id", "carrier_id"),
        Index("idx_task_planned_load_time", "planned_load_time"),
        {"comment": "运输任务单主表"},
    )
    __table_tier__ = "business"

    task_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="任务单号（租户内唯一）"
    )
    task_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="任务名称"
    )
    source: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="来源 1-手动 2-AI智能调度 3-导入",
    )

    # ===== 承运信息 =====
    carrier_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="承运类型 1-自有车 2-承运商 3-社会运力",
    )
    capacity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="自有运力 ID（biz_capacity.id）"
    )
    carrier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="承运商 ID（biz_carrier.id）"
    )
    social_driver_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="社会运力司机 ID（社会运力池模块落地后启用）"
    )

    # ===== 承运资源冷冻快照 =====
    main_driver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="主驾姓名（快照）"
    )
    main_driver_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="主驾电话（快照）"
    )
    main_driver_id_card: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="主驾身份证号（社会运力常用）"
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号（快照）"
    )
    trailer_plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="挂车车牌（快照）"
    )
    carrier_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="承运商名称（快照）"
    )
    carrier_short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="承运商简称（快照）"
    )

    # ===== 线路概要（首尾段冗余） =====
    origin: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="起点（段 1.from 冗余）"
    )
    origin_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="起点编码"
    )
    origin_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="起点行政区 ID"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="终点（末段.to 冗余）"
    )
    destination_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="终点编码"
    )
    destination_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="终点行政区 ID"
    )
    segment_count: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="分段数量"
    )

    # ===== 装载汇总 =====
    total_quantity: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="总台数（冗余）"
    )
    waybill_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联运单数（去重冗余）"
    )

    # ===== 时间 =====
    planned_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划装车时间（段 1）"
    )
    planned_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划到达时间（末段）"
    )
    actual_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际装车时间"
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="承运分配完成时间（-1→0/1）"
    )
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="派车完成时间（0→1 或分配直达已派车）"
    )
    actual_arrive_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际到达时间"
    )

    # ===== 承运成本 =====
    carrier_cost_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="承运成本总额"
    )
    carrier_cost_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="承运成本类型 1-包车 2-按台 3-按吨公里 4-其他",
    )
    cost_remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="成本备注"
    )

    # ===== 财务聚合冗余 =====
    prepaid_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="已预付金额（冗余）"
    )
    supplement_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="已补款金额（冗余）"
    )
    settled_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="已结算金额（冗余）"
    )
    contracted_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="已承包结算金额（冗余，承包单 doc_type=4 已支付合计）",
    )
    finance_doc_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="费用单数量（冗余）"
    )

    # ===== 财务锁定 / 绑定标记 =====
    is_locked: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否锁定 0-否 1-是（最终结算单/承运商结算单支付后置1，禁改成本字段）",
    )
    locked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="锁定时间"
    )
    locked_by_doc_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="锁定来源财务单据 ID"
    )
    is_recon_bound: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否已挂入承运商对账单（软标记，预留）",
    )
    is_payroll_bound: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否已挂入司机工资单（软标记，预留）",
    )
    payroll_settled: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="司机工资单是否已发放（冗余，预留）",
    )

    # ===== 状态与审计 =====
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-待派车 1-已派车 2-已装车 3-在途 4-已到达 "
                "5-已签收(聚合态) 7-已关闭 9-已取消",
    )
    dispatcher_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="调度员 user_id"
    )
    dispatcher_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="调度员姓名（冗余）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
