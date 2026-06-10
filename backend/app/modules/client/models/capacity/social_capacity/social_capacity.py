"""
社会运力主表（租户库）

社会运力是物流公司在自有车队 + 承运商均不够用时，从同行个体或同行 B 端
车辆一次性"打包登记"的临时承运单元（人 + 车 + 证照 + 结算）。

主表承载列表检索字段、双状态（审核 / 启用）、最近审核摘要、考核评级预留位。
详细的车辆 / 司机 / 证照 / 结算账户 / 审核流水分别落 4 张子表。
"""

from typing import Optional, Any
from datetime import datetime
from sqlalchemy import (
    String,
    SmallInteger,
    BigInteger,
    Integer,
    DateTime,
    Numeric,
    JSON,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SocialCapacity(TenantModelBase):
    """社会运力主表"""

    __tablename__ = "biz_social_capacity"
    __table_args__ = (
        Index("uk_social_code", "social_code", unique=True),
        Index("idx_driver_phone", "driver_phone"),
        Index("idx_plate_number", "plate_number"),
        Index("idx_approval_status", "approval_status"),
        Index("idx_status", "status"),
        {"comment": "社会运力主表"},
    )
    __table_tier__ = "business"

    social_code: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="社会运力编号 S{YYYY}{NNNNN}"
    )
    driver_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="驾驶员姓名（冗余检索）"
    )
    driver_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="驾驶员手机号（冗余检索 + 唯一性校验）"
    )
    driver_id_card: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="驾驶员身份证号（冗余）"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="车牌号（冗余检索 + 唯一性校验）"
    )
    vehicle_type_label: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="车辆类型快照（用于列表展示）"
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="来源（数据字典 social_capacity_source）"
    )
    source_remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="来源备注（引荐人 / 渠道）"
    )
    referrer_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="引荐人 user_id"
    )

    approval_status: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default="0",
        nullable=False,
        comment="审核状态 0-草稿 1-待审核 2-已通过 3-已驳回",
    )
    approval_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="最近一次审核人 user_id"
    )
    approval_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近一次审核时间"
    )
    approval_remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="最近一次审核意见 / 驳回理由"
    )

    approval_instance_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="审批中心实例 id（接入审批引擎后写回；为空表示走旧单级审核）",
    )

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default="0",
        nullable=False,
        comment="启用状态 0-未生效 1-正常 2-停用 3-黑名单",
    )
    status_remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="状态变更原因"
    )

    # 考核评级预留
    rating_score: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1), nullable=True, comment="预留：考核综合评分 0.0~5.0"
    )
    rating_level: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="预留：考核等级 1-A 2-B 3-C 4-D"
    )
    last_evaluated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="预留：最近一次考核时间"
    )
    evaluation_summary: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="预留：评级摘要快照"
    )
    order_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False, comment="预留：累计承运次数"
    )
    last_dispatched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="预留：最近一次派单时间"
    )

    created_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 user_id"
    )
    updated_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="最近修改人 user_id"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
