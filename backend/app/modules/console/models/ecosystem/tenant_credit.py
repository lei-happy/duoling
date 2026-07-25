"""服务平台租户信誉统计（平台库）

事件驱动增量更新 + 每日全量校准。1:1 于 ``sys_tenant``，懒加载创建。

存 ``eval_score_sum`` 而不只存 ``avg_score``，是为了让新增一条评价时能用
``eval_score_sum = eval_score_sum + ?, eval_count = eval_count + 1`` 原子递增
再算平均；否则每次新增评价都要重新聚合全表。

对外展示遵守最小样本量约束（见 constants.MIN_SAMPLES_FOR_*）：样本不足时
前端不展示完成率与评分，改显示「新加入」标签。
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, Numeric, SmallInteger, String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoTenantCredit(PlatformModelBase):
    """服务平台租户信誉统计"""

    __tablename__ = "sys_eco_tenant_credit"
    __table_args__ = (
        UniqueConstraint("tenant_code", name="uk_eco_credit_tenant"),
        Index("idx_eco_credit_whitelist", "audit_whitelist"),
        {"comment": "服务平台租户信誉统计"},
    )

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="租户编码"
    )

    # ===== 发布 =====
    publish_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计发布挂牌数"
    )
    listed_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计成功上架数"
    )

    # ===== 意向 =====
    intent_sent_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计发出意向数"
    )
    intent_received_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计收到意向数"
    )
    intent_responded_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计已响应意向数"
    )
    avg_respond_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="平均响应时长（分钟），用于展示「通常 2 小时内回复」",
    )

    # ===== 成交 =====
    deal_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计成交数"
    )
    deal_completed_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计完成数"
    )
    deal_terminated_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="累计终止数"
    )
    complete_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="履约完成率（%），成交数不足 5 时不对外展示",
    )

    # ===== 评价 =====
    eval_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="收到评价数"
    )
    eval_score_sum: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="评分累计和（支持原子递增）"
    )
    avg_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2), nullable=True,
        comment="平均评分，评价数不足 3 时不对外展示",
    )
    top_tags: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="高频好评标签（前 3 个）"
    )

    # ===== 违规 =====
    force_delist_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="被强制下架次数"
    )
    report_valid_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="被举报成立次数"
    )
    breach_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="爽约次数"
    )
    last_breach_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近爽约时间"
    )

    # ===== 免审白名单 =====
    audit_whitelist: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否免审白名单 0-否 1-是",
    )
    whitelist_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="进入白名单时间"
    )
    whitelist_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人（人工授予时）"
    )
    whitelist_source: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="来源 1-自动 2-人工"
    )
    # 记录移出时间是为了落地「移出后需重新累积 30 天无违规才能再次进入」
    # （04.运营审核与风控设计.md §2.2）。没有这个时间点，抽检发现问题移出的租户
    # 第二天就会被自动授予流程重新放进来，处置等于没有发生
    whitelist_revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近被移出白名单的时间"
    )
    whitelist_revoke_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="最近被移出白名单的原因"
    )

    # ===== 权限限制 =====
    publish_restricted_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="发布权限暂停至"
    )
    intent_restricted_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="意向权限暂停至"
    )

    # ===== 校准 =====
    last_calc_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后全量校准时间"
    )
