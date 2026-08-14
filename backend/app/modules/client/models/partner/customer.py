"""
客户管理表（租户库）
合作伙伴 - 客户（托运方/收货方）
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    BigInteger, Integer, Numeric, SmallInteger, String, Text, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Customer(TenantModelBase):
    """客户"""
    __tablename__ = "biz_customer"
    __table_args__ = {"comment": "客户表"}
    __table_tier__ = "business"

    customer_code: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, comment="客户编码"
    )
    customer_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="客户名称"
    )
    short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="客户简称"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, index=True,
        comment="默认经营主体ID（biz_business_entity.id），运单收入归属默认带出，空=租户默认主体",
    )
    customer_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="客户类型 0-主机厂 1-贸易商 2-经销商 3-个人 4-其他"
    )
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联系电话"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="地址"
    )
    settlement_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="结算方式 0-月结 1-票结 2-预付"
    )
    payment_days: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="账期天数（配合 settlement_type 推导到期日）；空=未设置，按 0 天算",
    )
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2), nullable=True,
        comment="信用额度（未收余额上限）；空=不限额。超额只预警不拦截",
    )
    credit_status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default=text("1"),
        comment="信用状态 0-暂停合作 1-正常 2-重点关注（仅作提示依据，不阻断业务）",
    )
    credit_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="统一社会信用代码"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
