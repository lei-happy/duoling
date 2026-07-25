"""服务平台违规举报（平台库，1.4 期）

举报与处置记录。举报成立会累加到被举报方的 ``sys_eco_tenant_credit``，
并可能触发强制下架、限制权限、关闭大厅能力等处置。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, JSON, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoReport(PlatformModelBase):
    """服务平台违规举报"""

    __tablename__ = "sys_eco_report"
    __table_args__ = (
        Index("idx_eco_report_status", "status", "created_at"),
        Index("idx_eco_report_reported", "reported_tenant_code", "status"),
        Index("idx_eco_report_reporter", "reporter_tenant_code", "status"),
        {"comment": "服务平台违规举报"},
    )

    report_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="举报编号"
    )
    target_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="举报对象 1-挂牌 2-成交 3-企业"
    )
    post_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联挂牌ID"
    )
    deal_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联成交单ID"
    )
    reported_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="被举报方租户"
    )
    reporter_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="举报方租户"
    )
    reporter_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="举报人 user_id"
    )
    reporter_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="举报人姓名"
    )
    report_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="类型 1-信息虚假 2-联系不上 3-恶意压价 4-骗取信息 "
                "5-爽约 6-违法违规 9-其他",
    )
    content: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="举报说明"
    )
    attachments: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="凭证附件URL数组"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-待处理 1-处理中 2-成立 3-不成立 4-证据不足",
    )
    handle_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="处理人（平台 user_id）"
    )
    handle_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处理时间"
    )
    handle_result: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="处理结论"
    )
    handle_action: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="处置动作 1-无 2-强制下架 3-警告 4-限制权限 5-关闭大厅能力",
    )
