"""
驾驶员核心身份表（租户库）

仅保留业务必须的身份字段，资质/运营/账户信息分别存储在关联表中。
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Driver(TenantModelBase):
    """驾驶员核心身份信息"""
    __tablename__ = "biz_driver"
    __table_args__ = {"comment": "驾驶员核心身份表"}
    __table_tier__ = "business"

    driver_code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, comment="司机编号（业务唯一标识）"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联的用户ID"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, index=True,
        comment="所属经营主体ID（biz_business_entity.id）",
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="姓名"
    )
    gender: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="性别 0-未知 1-男 2-女"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="手机号"
    )
    id_card: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="身份证号"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="头像URL"
    )
    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="紧急联系人姓名"
    )
    emergency_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="紧急联系人电话"
    )
    home_address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="家庭住址"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="人事状态 0-冻结 1-在职 2-离职"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
