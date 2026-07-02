"""
驾驶员承包结算配置表（租户库）

承接司机「结算模式」中的**承包制**（settlement_mode=1）：记录承包周期、承包费基准、
生效起止等参数，支持一名司机多期承包合同（历史合同保留、按生效区间取当期）。
统一管理 / 计件模式无需该配置，此表可空。
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime

from sqlalchemy import String, SmallInteger, BigInteger, Numeric, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverSettlementConfig(TenantModelBase):
    """驾驶员承包结算配置（承包制参数，支持一司机多期合同）"""

    __tablename__ = "biz_driver_settlement_config"
    __table_args__ = (
        Index("idx_dsc_driver_effective", "driver_id", "effective_start"),
        {"comment": "驾驶员承包结算配置表"},
    )
    __table_tier__ = "business"

    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="关联驾驶员ID"
    )
    period_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="承包周期类型 1-按月 2-按季 3-按年 4-自定义区间",
    )
    contract_base_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="承包费基准（每周期金额，>= 0）"
    )
    effective_start: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="承包合同生效起"
    )
    effective_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="承包合同生效止（空表示长期）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="状态 0-停用 1-生效",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
