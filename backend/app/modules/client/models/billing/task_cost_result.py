"""
任务成本计算结果（主表 + 费用明细表）

每次正式计算都新建一条主表行（is_active=1），并把同一任务上一条主表行
置为 is_active=0，从而保留计算快照便于审计与回放（与收入侧对称）。
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskCostResult(TenantModelBase):
    """任务成本计算结果主表（一次正式计算 = 一条快照）"""

    __tablename__ = "biz_task_cost_result"
    __table_args__ = (
        Index("idx_tcr_task", "task_id"),
        Index("idx_tcr_active", "task_id", "is_active"),
        Index("idx_tcr_calc_status", "calc_status"),
        Index("idx_tcr_calc_time", "calc_time"),
        {"comment": "任务成本计算结果主表"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务ID"
    )
    task_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="任务版本号（要素变更+1，用于识别过期结果）",
    )
    is_active: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="是否当前有效结果 0-否 1-是",
    )

    carrier_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="承运类型快照 1-自有车 2-承运商 3-社会运力",
    )
    payee_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="主收款方类型快照"
    )
    payee_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="主收款方ID快照（司机/承运商）"
    )
    payee_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="主收款方名称快照"
    )

    total_cost_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"), comment="成本合计（所有加项-扣减项）",
    )
    total_addition_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"), comment="加项合计",
    )
    total_deduction_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"), comment="扣减项合计",
    )

    calc_status: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="计算状态 success/partial/exception/locked",
    )
    calc_engine_version: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="成本引擎版本"
    )
    calc_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="计算时间"
    )
    triggered_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="触发来源 dispatch/manual_recalc/policy_changed/task_changed",
    )
    triggered_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="触发人"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="异常摘要"
    )


class TaskCostResultItem(TenantModelBase):
    """任务成本费用明细（每个费用项一行：司机运费/洗车费/装车费……）"""

    __tablename__ = "biz_task_cost_result_item"
    __table_args__ = (
        Index("idx_tcri_result", "result_id"),
        Index("idx_tcri_task", "task_id"),
        Index("idx_tcri_fee_type", "fee_type"),
        Index("idx_tcri_matched_rule", "matched_rule_id"),
        {"comment": "任务成本费用明细表"},
    )
    __table_tier__ = "business"

    result_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="成本结果主表ID"
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务ID"
    )

    fee_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="费用类型（字典 cost_fee_type）"
    )
    fee_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="费用名称（冗余）"
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="方向 1-加项 2-扣减项",
    )
    payee_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="收款方类型"
    )

    pricing_method: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="计价方式"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="匹配单价"
    )
    quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="计价数量（台/公里/趟/吨）"
    )
    distance_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="本次采用的里程"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"), comment="该费用项金额",
    )

    matched_policy_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="命中政策ID"
    )
    matched_rule_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="命中规则ID"
    )
    matched_rule_version: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="命中规则版本"
    )
    match_score: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="匹配得分"
    )
    match_trace_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="匹配过程JSON"
    )

    calc_status: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="计算状态 success/exception/skipped"
    )
    error_type: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="异常类型"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="异常信息"
    )
