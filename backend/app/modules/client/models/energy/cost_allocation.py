"""能源成本归集结果（租户库）"""

from decimal import Decimal
from datetime import date

from sqlalchemy import BigInteger, Date, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyCostAllocation(TenantModelBase):
    """能源成本归集结果（按维度 + 周期预聚合）"""

    __tablename__ = "biz_energy_cost_allocation"
    __table_args__ = (
        Index(
            "uk_energy_cost_alloc",
            "dimension", "dimension_id", "period_start", "energy_type",
            unique=True,
        ),
        Index("idx_energy_cost_alloc_period", "period_start", "period_end"),
        {"comment": "能源成本归集结果"},
    )
    __table_tier__ = "business"

    dimension: Mapped[str] = mapped_column(
        String(16), nullable=False,
        comment="维度 vehicle/driver/task/waybill/route/supplier",
    )
    dimension_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="维度对象 ID"
    )
    period_start: Mapped[date] = mapped_column(
        Date, nullable=False, comment="周期起"
    )
    period_end: Mapped[date] = mapped_column(
        Date, nullable=False, comment="周期止"
    )
    energy_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="能源类型"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="金额合计（仅 is_ledger_affecting=1）",
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=0, server_default=text("0"),
        comment="数量合计",
    )
    mileage: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default=text("0"),
        comment="里程合计（km）",
    )
    record_count: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default=text("0"),
        comment="流水笔数",
    )
