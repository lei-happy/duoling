"""能源卡绑定历史（租户库）

必须带 start_time / end_time，不能直接覆盖车辆/司机：
一笔历史消费要能还原当时这张卡绑的是哪辆车。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyCardBinding(TenantModelBase):
    """能源卡绑定历史"""

    __tablename__ = "biz_energy_card_binding"
    __table_args__ = (
        Index("idx_energy_card_binding_card", "card_id", "start_time"),
        Index("idx_energy_card_binding_vehicle", "vehicle_id"),
        Index("idx_energy_card_binding_driver", "driver_id"),
        {"comment": "能源卡绑定历史表"},
    )
    __table_tier__ = "business"

    card_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="能源卡 ID"
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="绑定车辆 ID"
    )
    driver_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="绑定司机 ID"
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="绑定开始时间"
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="绑定结束时间（空表示当前有效）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-已解绑 1-绑定中",
    )
