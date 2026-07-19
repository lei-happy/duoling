"""
意见反馈表
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, SmallInteger, BigInteger, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class Feedback(PlatformModelBase):
    """意见反馈"""
    __tablename__ = "sys_feedback"
    __table_args__ = {"comment": "意见反馈表"}

    tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, index=True, comment="租户编码"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="反馈用户ID"
    )
    user_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="提交时昵称快照"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联系电话"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="反馈标题"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="反馈内容"
    )
    feedback_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="反馈类型 0-建议 1-缺陷 2-投诉 3-其他"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="处理状态 0-待处理 1-处理中 2-已解决 3-已关闭"
    )
    reply: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="回复内容"
    )
    images: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="截图URL列表（JSON数组）"
    )
    handler_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="处理人平台用户ID"
    )
    handler_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="处理人姓名快照"
    )
    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近回复时间"
    )
