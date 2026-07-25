"""服务平台合作互评（平台库）

成交完成后双方互评，是信誉体系的主要输入。评价对外只展示客观事实
（完成率、平均分、高频标签），不合成单一「信用分」——合成分数看不出维度、
无法申诉，也容易被当作平台对企业的担保。详见 04.运营审核与风控设计.md §4.2。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, JSON, SmallInteger, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoEvaluation(PlatformModelBase):
    """服务平台合作互评"""

    __tablename__ = "sys_eco_evaluation"
    __table_args__ = (
        # 每方对同一笔成交只能评一次
        UniqueConstraint("deal_id", "from_tenant_code", name="uk_eco_eval"),
        Index("idx_eco_eval_to", "to_tenant_code", "created_at"),
        {"comment": "服务平台合作互评"},
    )

    deal_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="成交单ID（sys_eco_deal.id）"
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（冗余）"
    )
    from_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="评价方租户"
    )
    from_tenant_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="评价方企业名（快照）"
    )
    to_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="被评价方租户"
    )
    role: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="评价角色 1-货主评承运 2-承运评货主",
    )
    score: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="评分 1~5"
    )
    tags: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="评价标签数组"
    )
    content: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="文字评价"
    )
    is_default: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否超时默认好评 0-否 1-是",
    )
    reply: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="被评方回复（仅一次）"
    )
    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="回复时间"
    )
