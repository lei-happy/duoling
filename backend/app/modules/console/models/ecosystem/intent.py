"""服务平台合作意向（平台库）

一次「我想接这单」或「我想用这台车」的表达。发起意向是本模块唯一的付费能力
（``ecosystem_intent``，仅 pro 版本），而**响应意向对全版本开放**——付费门槛
卡在主动发起，绝不能卡在被动响应，否则 standard 租户的发布权就是废的。
详见 00.模块总览.md §5.2。

联系方式的双向解锁发生在挂牌方响应之后（status → TALKING）。在此之前双方
都看不到对方的手机号，这是「先表达意愿、再交换信息」的设计，用于降低骚扰。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoIntent(PlatformModelBase):
    """服务平台合作意向"""

    __tablename__ = "sys_eco_intent"
    __table_args__ = (
        Index("idx_eco_intent_post", "post_id", "status"),
        # 挂牌方查「我收到的意向」
        Index("idx_eco_intent_owner", "owner_tenant_code", "status", "created_at"),
        # 发起方查「我发出的意向」
        Index("idx_eco_intent_initiator",
              "initiator_tenant_code", "status", "created_at"),
        # 「同一租户对同一挂牌只能有一个有效意向」的判重查询。
        # 刻意不建唯一索引：撤回或失效后应允许重新发起，唯一索引会把历史记录
        # 也算进去。改为应用层查 status IN (0,1,2) 判重。
        Index("idx_eco_intent_dup", "post_id", "initiator_tenant_code", "status"),
        {"comment": "服务平台合作意向"},
    )

    # ===== 身份 =====
    intent_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="意向编号"
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )
    post_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="挂牌类型（冗余）"
    )
    owner_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="挂牌归属租户（冗余，避免查「我收到的」时 join 主表）",
    )
    initiator_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="发起方租户"
    )
    initiator_tenant_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="发起方企业全称（快照）"
    )
    initiator_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="发起人 user_id"
    )
    initiator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发起人姓名"
    )

    # ===== 状态 =====
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-待响应 1-洽谈中 2-已选定 3-已婉拒 4-已撤回 5-已失效",
    )

    # ===== 报价与能力 =====
    offer_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="报价"
    )
    price_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="计价方式 1-包车 2-按台 3-按公里 4-面议"
    )
    price_include_tax: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否含税 0-否 1-是"
    )
    accept_quantity: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="可承接量"
    )
    capability_desc: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        comment="能力描述（货源侧=可安排车型数量；运力侧=货物描述）",
    )
    available_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="可配合时间起"
    )
    available_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="可配合时间止"
    )
    ref_post_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="关联发起方自己的挂牌ID（两个大厅互引，可省一轮沟通）",
    )

    # ===== 联系方式与解锁 =====
    contact_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="发起方联系人"
    )
    contact_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="发起方联系电话"
    )
    contact_unlocked: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="联系方式是否已双向解锁 0-否 1-是",
    )
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="解锁时间"
    )

    # ===== 留言 =====
    message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="首次附言（需过敏感内容拦截）"
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后留言时间"
    )
    unread_owner: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="挂牌方未读留言数"
    )
    unread_initiator: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="发起方未读留言数"
    )

    # ===== 流转时间 =====
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="响应时间（用于响应速度统计）"
    )
    declined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="婉拒时间"
    )
    decline_reason: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="婉拒原因 1-价格不合适 2-时间对不上 3-车型不匹配 4-已选其他 9-其他",
    )
    decline_remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="婉拒补充说明"
    )
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="撤回时间"
    )
    invalid_reason: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="失效原因 1-挂牌被他人成交 2-挂牌已下架 3-挂牌已过期",
    )
    selected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="被选定时间"
    )


class SysEcoIntentMessage(PlatformModelBase):
    """服务平台洽谈留言

    留言内容同样要过敏感内容硬拦截。虽然洽谈层已解锁联系方式，但留言里塞微信号
    绕过平台的行为仍需拦住——理由是留言可能发生在解锁之前。
    """

    __tablename__ = "sys_eco_intent_message"
    __table_args__ = (
        Index("idx_eco_msg_intent", "intent_id", "created_at"),
        {"comment": "服务平台洽谈留言"},
    )

    intent_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="意向ID（sys_eco_intent.id）"
    )
    sender_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="发送方租户"
    )
    sender_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="发送人 user_id"
    )
    sender_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发送人姓名"
    )
    content: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="留言内容"
    )
    attachments: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="附件URL数组"
    )
    is_read: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="对方是否已读 0-否 1-是"
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="已读时间"
    )
