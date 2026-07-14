"""
产品更新日志表
"""

from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, SmallInteger, Text, Date, BigInteger, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class Changelog(PlatformModelBase):
    """产品更新日志"""
    __tablename__ = "sys_changelog"
    __table_args__ = {"comment": "产品更新日志表"}

    version: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="版本号（如 v1.2.0）"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="更新标题"
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="更新内容（Markdown 格式）"
    )
    release_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="发布日期"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号（越大越靠前）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-已发布"
    )
    is_popup: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default="0",
        comment="租户端是否弹框强提醒 0-否 1-是",
    )


class ChangelogRead(PlatformModelBase):
    """租户端用户版本升级说明已读记录（用于弹框只弹一次）"""
    __tablename__ = "sys_changelog_read"
    __table_args__ = (
        Index("uk_changelog_user", "changelog_id", "user_id", unique=True),
        {"comment": "版本升级说明用户已读记录表"},
    )

    changelog_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="更新记录ID"
    )
    tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="租户编码（冗余，便于统计）"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="用户ID"
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="已读时间"
    )
