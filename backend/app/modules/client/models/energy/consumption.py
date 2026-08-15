"""能源消费标准流水（租户库）"""

from decimal import Decimal
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON, BigInteger, DateTime, Index, Numeric, SmallInteger, String, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyConsumption(TenantModelBase):
    """能源消费标准流水"""

    __tablename__ = "biz_energy_consumption"
    __table_args__ = (
        Index("uk_energy_consumption_no", "consumption_no", unique=True),
        Index("idx_energy_cons_time", "consumption_time"),
        Index("idx_energy_cons_account", "account_id"),
        Index("idx_energy_cons_vehicle", "vehicle_id"),
        Index("idx_energy_cons_driver", "driver_id"),
        Index("idx_energy_cons_task", "task_id"),
        Index("idx_energy_cons_match", "match_status"),
        {"comment": "能源消费标准流水表"},
    )
    __table_tier__ = "business"

    consumption_no: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="消费单号"
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="供应商 ID"
    )
    station_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="站点 ID"
    )
    station_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="站点名称（快照）"
    )
    account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="能源账户 ID"
    )
    card_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="能源卡 ID"
    )
    card_no: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="卡号（快照）"
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="车辆 ID"
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号（快照）"
    )
    driver_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="司机 ID"
    )
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="司机姓名（快照）"
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="任务 ID"
    )
    waybill_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="运单 ID"
    )
    route_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="线路 ID"
    )
    energy_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="能源类型 OIL/GAS/ELECTRIC/OTHER"
    )
    energy_product_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="能源商品 ID"
    )
    product_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="商品名称（快照）"
    )
    quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4), nullable=True, comment="数量"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="单位"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 6), nullable=True, comment="单价"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, comment="金额"
    )
    mileage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="本次行驶里程（km）"
    )
    odometer: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, comment="表显里程"
    )
    consumption_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="消费时间"
    )
    external_transaction_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="外部流水号"
    )
    source_channel: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=3, server_default=text("3"),
        comment="来源 1-供应商直连 2-Excel 3-手工 4-司机垫付引用 5-月结账单",
    )
    is_ledger_affecting: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="是否扣减能源账户余额 0-否 1-是（垫付引用置 0，避免与任务费用单重复）",
    )
    match_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="UNMATCHED",
        server_default=text("'UNMATCHED'"),
        comment="匹配状态 MATCHED/PARTIAL/UNMATCHED/CONFLICT",
    )
    match_trace_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="匹配轨迹"
    )
    recon_status: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="对账状态"
    )
    exception_status: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="异常状态"
    )
    raw_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="原始数据 ID"
    )
    ledger_txn_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="扣账流水 ID"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="备注"
    )
