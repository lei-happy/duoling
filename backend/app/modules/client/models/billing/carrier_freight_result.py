"""
承运商运费计算结果（主表 + 车型明细表）

每次正式计算都新建一条主表行（is_active=1），并把同一任务上一条主表行
置为 is_active=0，从而保留计算快照便于审计与回放（与收入侧对称）。
计算粒度为「任务」，明细按任务内车型分组各一行。
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


class CarrierFreightResult(TenantModelBase):
    """承运商运费计算结果主表（一次正式计算 = 一条快照）"""

    __tablename__ = "biz_carrier_freight_result"
    __table_args__ = (
        Index("idx_cfr_task", "task_id"),
        Index("idx_cfr_active", "task_id", "is_active"),
        Index("idx_cfr_carrier", "carrier_id"),
        Index("idx_cfr_calc_status", "calc_status"),
        Index("idx_cfr_calc_time", "calc_time"),
        {"comment": "承运商运费计算结果主表"},
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

    carrier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="承运商ID快照"
    )
    carrier_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="承运商名称快照"
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"), comment="承运运费合计",
    )

    calc_status: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="计算状态 success/partial/exception/locked",
    )
    calc_engine_version: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="承运运费引擎版本"
    )
    calc_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="计算时间"
    )
    triggered_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="触发来源 dispatch/manual_recalc/contract_changed/rule_changed/task_changed",
    )
    triggered_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="触发人"
    )
    matched_contract_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="主命中合同ID（首条 success 行）"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="异常摘要"
    )


class CarrierFreightResultDetail(TenantModelBase):
    """承运商运费计算结果明细（任务内每个车型分组一行）"""

    __tablename__ = "biz_carrier_freight_result_detail"
    __table_args__ = (
        Index("idx_cfrd_result", "result_id"),
        Index("idx_cfrd_task", "task_id"),
        Index("idx_cfrd_rule", "matched_rule_id"),
        {"comment": "承运商运费计算结果明细表"},
    )
    __table_tier__ = "business"

    result_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="计算结果主表ID"
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务ID"
    )

    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="品牌ID"
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="车系ID"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="品牌名称（冗余）"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车型名称（冗余）"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="台数",
    )

    matched_contract_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="匹配的合同ID"
    )
    matched_rule_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="匹配的承运价规则ID"
    )
    matched_rule_version: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="匹配规则版本号"
    )

    origin_match_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="实际命中的出发地行政区ID"
    )
    origin_match_level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="出发地命中层级 province/city/district/custom"
    )
    destination_match_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="实际命中的目的地行政区ID"
    )
    destination_match_level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="目的地命中层级"
    )
    direction: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="方向 forward/backward"
    )
    model_match_type: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="车型命中层级 series/brand/general"
    )

    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="单价"
    )
    billing_mode: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="计费模式快照"
    )
    distance_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="公里数快照（单公里计费时）"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"),
        server_default=text("0"), comment="本明细计算金额",
    )

    match_score: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="匹配综合评分"
    )
    match_trace_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="匹配过程留痕（候选地区链/车型层级/方向/评分明细等）"
    )

    calc_status: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="计算状态 success/exception"
    )
    error_type: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="异常类型"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="异常描述"
    )
