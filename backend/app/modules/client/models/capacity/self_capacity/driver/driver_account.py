"""
驾驶员账户结算表（租户库）

与 biz_driver 1:N 关联，一个驾驶员可拥有多个结算账户。
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy import String, SmallInteger, BigInteger, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverAccount(TenantModelBase):
    """驾驶员账户结算"""
    __tablename__ = "biz_driver_account"
    __table_args__ = {"comment": "驾驶员账户结算表"}
    __table_tier__ = "business"

    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="关联驾驶员ID"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="所属企业ID（经营主体）"
    )
    account_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="账户类型 1-银行卡 2-油气款 3-积分"
    )
    account_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="账户名称"
    )
    account_no: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="账户号"
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, comment="账户余额"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
