"""
平台司机表（汇总各租户司机摘要）
"""

from sqlalchemy import String, SmallInteger, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysDriver(PlatformModelBase):
    """平台司机（汇总各租户司机摘要）"""
    __tablename__ = "sys_driver"
    __table_args__ = {"comment": "平台司机表（汇总各租户司机摘要）"}

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="租户编码"
    )
    biz_driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="租户库 biz_driver.id"
    )
    driver_code: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="司机编号"
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="姓名"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="手机号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="人事状态 0-冻结 1-在职 2-离职"
    )
