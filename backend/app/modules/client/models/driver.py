"""
驾驶员信息表（租户库）
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, SmallInteger, Date, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Driver(TenantModelBase):
    """驾驶员信息"""
    __tablename__ = "biz_driver"
    __table_args__ = {"comment": "驾驶员信息表"}
    __table_tier__ = "business"

    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联的用户ID"
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="姓名"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="手机号"
    )
    id_card: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="身份证号"
    )
    gender: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="性别 0-未知 1-男 2-女"
    )
    license_type: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, comment="驾照类型（A1/A2/B1/B2/C1等）"
    )
    license_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="驾驶证号"
    )
    license_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="驾驶证到期日"
    )
    qualification_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="从业资格证号"
    )
    qualification_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="从业资格证到期日"
    )
    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="紧急联系人"
    )
    emergency_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="紧急联系电话"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="头像URL"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-在岗 2-休息 3-离职"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
