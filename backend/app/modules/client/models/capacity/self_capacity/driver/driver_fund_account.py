"""
驾驶员资金账户（往来账户，租户库）

与既有 ``biz_driver_account``（收款账户/银行卡）是**不同概念**：本表是司机与公司
之间的资金往来台账/钱包，一个司机 × 一个经营主体唯一一账；``balance`` 为带符号净额
（以司机视角：正=公司欠司机，负=司机欠公司），且只能通过资金流水
``biz_driver_fund_transaction`` 改变。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Numeric, SmallInteger, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverFundAccount(TenantModelBase):
    """驾驶员资金账户（往来账）"""

    __tablename__ = "biz_driver_fund_account"
    __table_args__ = (
        UniqueConstraint(
            "driver_id", "enterprise_id", name="uk_dfa_driver_ent"
        ),
        {"comment": "驾驶员资金账户（往来账）"},
    )
    __table_tier__ = "business"

    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="关联 biz_driver.id"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="所属经营主体ID"
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", nullable=False,
        comment="当前净余额（带符号：正=公司欠司机 负=司机欠公司）",
    )
    frozen_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", nullable=False,
        comment="冻结金额（抵扣中/审批中占用，二期启用）",
    )
    total_in: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=0, server_default="0", nullable=False,
        comment="累计入账（对账用）",
    )
    total_out: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=0, server_default="0", nullable=False,
        comment="累计出账（对账用）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", nullable=False,
        comment="状态 1-正常 0-冻结（冻结后禁止新流水）",
    )
    last_txn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近一笔流水时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
