"""
资金账户（往来账户，租户库）

收款方资金往来台账/钱包，按 ``(owner_type, owner_id, enterprise_id)`` 唯一定位：
  * ``owner_type=1`` 自有司机，``owner_id`` = ``biz_driver.id``
  * ``owner_type=3`` 社会运力，``owner_id`` = ``biz_social_capacity.id``
  * ``owner_type=2`` 承运商（预留）

与既有 ``biz_driver_account``（收款账户/银行卡）是**不同概念**：本表是收款方与公司
之间的资金往来台账/钱包；``balance`` 为带符号净额（以收款方视角：正=公司欠对方，
负=对方欠公司），且只能通过资金流水 ``biz_driver_fund_transaction`` 改变。
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
    """资金账户（往来账，收款方泛化）"""

    __tablename__ = "biz_driver_fund_account"
    __table_args__ = (
        UniqueConstraint(
            "owner_type", "owner_id", "enterprise_id", name="uk_dfa_owner_ent"
        ),
        {"comment": "资金账户（往来账，收款方泛化）"},
    )
    __table_tier__ = "business"

    owner_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1",
        comment="收款方类型 1-自有司机 2-承运商(预留) 3-社会运力",
    )
    owner_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True,
        comment="收款方ID：owner_type=1时为biz_driver.id，=3时为biz_social_capacity.id",
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
