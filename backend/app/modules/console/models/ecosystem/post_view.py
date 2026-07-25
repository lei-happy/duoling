"""服务平台挂牌浏览统计（平台库）

按「挂牌 + 查看企业 + 日期」聚合，不记录每一次点击，把量级从千万压到百万。

存在的意义是给发布方看到需求侧热度（「本周有 12 家同行看过这条信息」）。
这对 standard 租户尤其重要：它们能发布但不能主动发起意向，挂牌可能一段时间
无人问询，需要这个反馈避免「发了没用」的挫败感。
详见 05.前端交互与UX设计.md §7.3。

写入用 ``INSERT ... ON DUPLICATE KEY UPDATE view_count = view_count + 1``
一条 SQL 完成，无需先查后写。发布方查看自己的挂牌不计入统计。
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Date, DateTime, Index, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoPostView(PlatformModelBase):
    """服务平台挂牌浏览统计"""

    __tablename__ = "sys_eco_post_view"
    __table_args__ = (
        UniqueConstraint(
            "post_id", "viewer_tenant_code", "view_date", name="uk_eco_view"
        ),
        Index("idx_eco_view_owner", "owner_tenant_code", "view_date"),
        Index("idx_eco_view_post", "post_id", "view_date"),
        {"comment": "服务平台挂牌浏览统计"},
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )
    owner_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="挂牌归属租户（冗余，发布方查询用）"
    )
    viewer_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="查看方租户"
    )
    viewer_province: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        comment="查看方所在省（聚合展示用，不暴露具体企业）",
    )
    viewer_city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="查看方所在市"
    )
    view_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="统计日期"
    )
    view_count: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", comment="当日浏览次数"
    )
    first_viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="首次浏览时间"
    )
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后浏览时间"
    )
