"""
首页推广位 Banner 相关平台库模型

- PromotionBanner：Banner 配置（Console 配置，Client 展示）
- PromotionBannerEvent：曝光/点击埋点明细（跨租户集中存储，便于 Console 聚合）
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, SmallInteger, BigInteger, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class PromotionBanner(PlatformModelBase):
    """首页推广位 Banner 配置"""

    __tablename__ = "sys_promotion_banner"
    __table_args__ = {"comment": "首页推广位 Banner 配置表"}

    title: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="内部标题/运营备注名"
    )
    image_url: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="图片地址"
    )
    link_type: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="none",
        comment="跳转类型 none-只看不跳 external-外链 internal-站内路由",
    )
    link_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="跳转地址（link_type=none 时为空）"
    )
    open_in_new_tab: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="外链是否新标签打开 0-否 1-是",
    )
    target_type: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="all",
        comment="投放定向 all-全部 version-按产品版本 tenant-指定租户",
    )
    target_values: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True,
        comment="定向白名单：version_code 列表或 tenant_code 列表",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="轮播排序，小在前"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="draft",
        comment="状态 draft-草稿 published-上线 offline-下线",
    )
    start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="生效时间（NULL 不限）"
    )
    end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="失效时间（NULL 不限）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="配置人用户ID"
    )


class PromotionBannerEvent(PlatformModelBase):
    """推广位 Banner 曝光/点击埋点明细"""

    __tablename__ = "sys_promotion_banner_event"
    __table_args__ = (
        Index("idx_banner_event", "banner_id", "event_type", "occurred_at"),
        Index("idx_tenant_event", "tenant_code", "occurred_at"),
        {"comment": "推广位 Banner 埋点明细表"},
    )

    banner_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="Banner ID"
    )
    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="租户编码"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="用户ID"
    )
    user_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="用户手机号（冗余，便于展示）"
    )
    event_type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="事件类型 view-曝光 click-点击"
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="发生时间"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="User-Agent（排查用）"
    )
