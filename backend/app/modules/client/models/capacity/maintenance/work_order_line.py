"""维保工单明细行"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetWorkOrderLine(TenantModelBase):
    """工单明细

    line_type: labor | part | other
    """

    __tablename__ = "biz_fleet_work_order_line"
    __table_args__ = (
        Index("idx_fleet_wo_line_wo", "work_order_id", "sort_order"),
        {"comment": "车辆维保工单明细行"},
    )
    __table_tier__ = "business"

    work_order_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="工单ID"
    )
    line_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="labor/part/other"
    )
    part_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="备件ID"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="项目/备件名称"
    )
    qty: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=1, server_default=text("1"),
        comment="数量",
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="单价"
    )
    labor_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2), nullable=True, comment="工时（小时）"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0, server_default=text("0"),
        comment="行金额",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="排序",
    )
