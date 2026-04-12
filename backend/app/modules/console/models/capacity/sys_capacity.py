"""
平台运力表（汇总各租户运力数据）
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, SmallInteger, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysCapacity(PlatformModelBase):
    """平台运力（汇总各租户司机-车辆绑定关系）"""
    __tablename__ = "sys_capacity"
    __table_args__ = {"comment": "平台运力表（汇总各租户运力数据）"}

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="租户编码"
    )
    biz_capacity_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="租户库 biz_capacity.id"
    )
    driver_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="司机姓名"
    )
    driver_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="司机手机号"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 1-绑定中 0-已解绑"
    )
    bound_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="绑定时间"
    )
    unbound_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="解绑时间"
    )
