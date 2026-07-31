"""备件库存流水"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FleetStockTxn(TenantModelBase):
    """库存流水

    txn_type: in | out | adjust
    ref_type: work_order | inbound | adjust | null
    """

    __tablename__ = "biz_fleet_stock_txn"
    __table_args__ = (
        Index("idx_fleet_stock_txn_part", "part_id", "created_at"),
        Index("idx_fleet_stock_txn_ref", "ref_type", "ref_id"),
        {"comment": "车辆备件库存流水"},
    )
    __table_tier__ = "business"

    part_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="备件ID"
    )
    part_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="备件编码（冗余）"
    )
    part_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="备件名称（冗余）"
    )
    txn_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="in/out/adjust"
    )
    qty: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="变动数量（正数）"
    )
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="单价"
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="金额"
    )
    ref_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="关联类型"
    )
    ref_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联单据ID"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人"
    )
