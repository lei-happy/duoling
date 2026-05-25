"""
社会运力 - 司机详情表（租户库）

与 biz_social_capacity 1:1 关联，存储驾驶员基础信息与证照信息。
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, SmallInteger, BigInteger, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SocialCapacityDriver(TenantModelBase):
    """社会运力司机详情"""

    __tablename__ = "biz_social_capacity_driver"
    __table_args__ = {"comment": "社会运力司机详情表"}
    __table_tier__ = "business"

    social_capacity_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, comment="关联 biz_social_capacity.id"
    )

    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="姓名"
    )
    gender: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="性别 0-未知 1-男 2-女"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="手机号"
    )
    id_card: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="身份证号"
    )
    birth_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="出生日期"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="头像 URL"
    )

    # 资质
    license_type: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, comment="驾驶证类型 A1/A2/B1/B2/C1"
    )
    license_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="驾驶证号"
    )
    license_issue_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="驾驶证初次领证日期"
    )
    license_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="驾驶证有效期"
    )
    license_class: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="准驾车型"
    )
    qualification_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="从业资格证号"
    )
    qualification_expire: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="从业资格证有效期"
    )

    # 证照影像
    license_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="驾驶证照片 URL"
    )
    qualification_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="从业资格证照片 URL"
    )
    id_card_front_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="身份证正面 URL"
    )
    id_card_back_photo: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="身份证反面 URL"
    )

    # 其他
    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="紧急联系人"
    )
    emergency_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="紧急联系电话"
    )
    home_address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="居住地址"
    )
