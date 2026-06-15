"""
证照到期预警表（租户库）

由「证照监控引擎」（独立 worker）周期性扫描各类运力资质到期字段后写入。
本表是预警的「物化结果」，前端合规看板 / 列表预警 / 工作台提醒均读此表，
避免每次都现算，也便于记录「已忽略 / 已处理」状态。

一条预警 = 某个主体（司机 / 车辆 / 社会运力）的某一类证照（doc_type）的
最新到期状态。同一主体同一证照在「未删除」范围内只保留一条，扫描时 upsert。
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizComplianceAlert(TenantModelBase):
    """证照到期预警

    subject_type:
      - driver          : 自有驾驶员
      - vehicle         : 自有车辆
      - social_driver   : 社会运力-司机
      - social_vehicle  : 社会运力-车辆
    doc_type:
      - driver_license      : 驾驶证
      - qualification       : 从业资格证
      - insurance           : 保险
      - inspection          : 年检
      - transport_license   : 道路运输证
    level:
      - expired   : 已过期（days_left < 0）
      - critical  : 临界（0 <= days_left <= critical 阈值）
      - warning   : 预警（critical < days_left <= horizon 阈值）
    status:
      - open      : 待处理（默认）
      - dismissed : 已忽略（人工忽略，扫描不再覆盖其状态）
      - resolved  : 已消除（续期 / 删除后，扫描自动置为）
    """

    __tablename__ = "biz_compliance_alert"
    __table_args__ = (
        Index(
            "idx_ca_subject_doc",
            "subject_type",
            "subject_id",
            "doc_type",
        ),
        Index("idx_ca_level_status", "level", "status"),
        Index("idx_ca_expire", "expire_date"),
        {"comment": "证照到期预警表"},
    )
    __table_tier__ = "business"

    subject_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="主体类型 driver/vehicle/social_driver/social_vehicle"
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="主体业务ID（驾驶员ID/车辆ID/社会运力ID）"
    )
    subject_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="主体名称（司机姓名 / 车牌号）"
    )
    subject_ref: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="主体辅助标识（司机手机号 / 车牌号）"
    )

    doc_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="证照类型 driver_license/qualification/insurance/inspection/transport_license",
    )
    doc_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="证照号（如有）"
    )

    expire_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="到期日"
    )
    days_left: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="距到期天数（负数表示已过期）"
    )
    level: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="warning",
        server_default=text("'warning'"),
        comment="预警级别 expired/critical/warning",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="open",
        server_default=text("'open'"),
        comment="处理状态 open/dismissed/resolved",
    )

    dismissed_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="忽略操作人 user_id"
    )
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="忽略时间"
    )

    first_alerted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="首次预警时间"
    )
    last_scan_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="最近一次扫描命中时间"
    )
