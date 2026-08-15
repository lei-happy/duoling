"""能源卡（租户库）"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyCard(TenantModelBase):
    """能源卡"""

    __tablename__ = "biz_energy_card"
    __table_args__ = (
        Index("uk_energy_card_no", "card_no", unique=True),
        Index("idx_energy_card_account", "account_id"),
        {"comment": "能源卡表"},
    )
    __table_tier__ = "business"

    account_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="所属能源账户 ID"
    )
    card_no: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="卡号（租户内唯一）"
    )
    external_card_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="供应商侧卡 ID"
    )
    card_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="卡类型（实体卡/虚拟卡等）"
    )
    energy_type: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="能源类型 OIL/GAS/ELECTRIC/OTHER"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-正常 2-冻结 3-已注销 4-挂失 5-未激活",
    )
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="有效期起"
    )
    valid_to: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="有效期止"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
