"""服务平台订阅提醒（平台库，1.4 期）

按线路/车型订阅新挂牌，命中后推送站内待办或短信。

``last_matched_post_id`` 作为增量扫描游标：Worker 每次只处理
``post.id > last_matched_post_id`` 的新挂牌，既避免重复通知，也避免每次全表比对。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoSubscription(PlatformModelBase):
    """服务平台订阅提醒"""

    __tablename__ = "sys_eco_subscription"
    __table_args__ = (
        Index("idx_eco_sub_tenant", "tenant_code", "enabled"),
        # 推送 Worker 扫描
        Index("idx_eco_sub_scan", "enabled", "post_type"),
        {"comment": "服务平台订阅提醒"},
    )

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="租户编码"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 user_id"
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="订阅名称"
    )
    post_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="订阅类型 1-货源 2-运力"
    )
    from_provinces: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="出发地省数组"
    )
    from_cities: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="出发地市数组"
    )
    to_provinces: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="目的地省数组"
    )
    to_cities: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="目的地市数组"
    )
    filter_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="其余筛选条件原样保存"
    )
    notify_channel: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="通知渠道 1-待办 2-待办+短信",
    )
    enabled: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否启用 0-否 1-是"
    )
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后通知时间"
    )
    last_matched_post_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="最后命中的挂牌ID（增量扫描游标）"
    )
    matched_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计命中数"
    )
