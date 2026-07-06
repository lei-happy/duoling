"""
运力表（租户库）

biz_capacity: 记录司机与车辆的当前绑定关系
biz_capacity_log: 记录每次上车/下车的变动历史
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Capacity(TenantModelBase):
    """运力（司机-车辆绑定关系）"""
    __tablename__ = "biz_capacity"
    __table_args__ = {"comment": "运力表（司机-车辆绑定关系）"}
    __table_tier__ = "business"

    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, index=True,
        comment="所属经营主体ID（biz_business_entity.id）",
    )
    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联司机ID"
    )
    driver_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="司机姓名（冗余）"
    )
    driver_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="司机手机号（冗余）"
    )
    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联车辆ID"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号（冗余）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 1-绑定中 0-已解绑"
    )
    operation_status: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        server_default="1",
        nullable=False,
        comment="运力运营状态 1-可接单 2-运输中 3-休假 4-停运 5-维修保养",
    )
    bound_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="绑定（上车）时间"
    )
    unbound_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="解绑（下车）时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )


class CapacityLog(TenantModelBase):
    """运力变动记录"""
    __tablename__ = "biz_capacity_log"
    __table_args__ = {"comment": "运力变动记录表"}
    __table_tier__ = "business"

    capacity_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联运力ID"
    )
    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="司机ID"
    )
    driver_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="司机姓名"
    )
    vehicle_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="车辆ID"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号"
    )
    action: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="操作类型 1-上车(绑定) 2-下车(解绑)"
    )
    action_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="操作时间"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人ID"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
