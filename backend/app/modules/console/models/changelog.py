"""
产品更新日志表
"""

from datetime import date
from typing import Optional
from sqlalchemy import String, SmallInteger, Text, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.base import PlatformModelBase


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
