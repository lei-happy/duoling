"""
驾驶员资质信息表（租户库）

与 biz_driver 1:1 关联，存储驾驶证和从业资格证信息。
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, BigInteger, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverLicense(TenantModelBase):
    """驾驶员资质信息"""
    __tablename__ = "biz_driver_license"
    __table_args__ = {"comment": "驾驶员资质信息表"}
    __table_tier__ = "business"

    driver_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, comment="关联驾驶员ID"
    )
    license_type: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, comment="驾驶证类型（A1/A2/B1/B2/C1等）"
    )
    license_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="驾驶证号"
    )
    license_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="驾驶证有效期"
    )
    qualification_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="从业资格证号"
    )
    qualification_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="从业资格证有效期"
    )
    license_photo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="驾驶证照片URL"
    )
    qualification_photo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="从业资格证照片URL"
    )
    id_card_front_photo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="身份证正面照片URL"
    )
    id_card_back_photo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="身份证反面照片URL"
    )
