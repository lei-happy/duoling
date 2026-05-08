"""
承运商结算账户表（租户库）
一个承运商可以挂多个结算账户（对公主账户、私户司机、不同业务线等）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, BigInteger, Integer, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CarrierSettlement(TenantModelBase):
    """承运商结算账户"""
    __tablename__ = "biz_carrier_settlement"
    __table_args__ = (
        Index("idx_carrier_id", "carrier_id"),
        Index("idx_carrier_default", "carrier_id", "is_default", "status"),
        {"comment": "承运商结算账户表"},
    )
    __table_tier__ = "business"

    carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier.id"
    )
    account_label: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="账户标签（如对公主账户/私户-司机张三/运输专用账户）",
    )
    account_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="账户类型 0-对公 1-对私 2-其他",
    )
    settlement_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="结算方式 0-月结 1-票结 2-预付 3-趟结",
    )
    settlement_period: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="月结/趟结周期天数（票结/预付场景为空）"
    )
    settlement_day: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="月结结账日（每月几号 1-28，预留）"
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户行"
    )
    bank_branch: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户支行"
    )
    bank_account: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="银行账号"
    )
    bank_account_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="户名"
    )
    swift_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联行号（可选）"
    )
    tax_rate: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="税率 %（远期，结合发票）"
    )
    applicable_scope: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="适用范围（业务线/路线/车型，文本备注）"
    )
    is_default: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否默认账户 1-是 0-否（同 carrier_id 内最多 1 条 is_default=1）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="状态 0-停用 1-正常",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="排序"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
