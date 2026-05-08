"""
承运商邀请流水表（租户库）
本期 Phase B 仅使用路径 B 字段；C1/C2/C3 字段全部预留
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, SmallInteger, Text, BigInteger, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CarrierInvitation(TenantModelBase):
    """承运商邀请流水"""
    __tablename__ = "biz_carrier_invitation"
    __table_args__ = (
        Index("idx_carrier_id", "carrier_id"),
        Index("idx_invite_phone", "invite_phone"),
        Index("idx_status_expires", "status", "expires_at"),
        Index("idx_pending_a_review", "pending_a_review", "status"),
        {"comment": "承运商邀请流水表"},
    )
    __table_tier__ = "business"

    carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier.id"
    )
    invite_code: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="邀请码（短链 URL，全局唯一）"
    )
    invite_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="被邀请人手机号"
    )
    expected_carrier_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="A 录入承运商档案时的名称快照"
    )
    invite_channel: Mapped[str] = mapped_column(
        String(20), default="sms", server_default="sms",
        comment="sms / wechat / link",
    )
    sms_content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="短信内容快照（便于审计与追责）"
    )
    invite_token: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="一次性激活 token（hash 后存储）"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="失效时间，default now()+7d"
    )
    invite_path: Mapped[str] = mapped_column(
        String(8), nullable=False, comment="路径分支：B / C1 / C2 / C3"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="0-待发送 1-已发送 2-已点击 3-已激活 4-已过期 "
                "5-A 已撤回 6-B 已拒绝 7-代转交中 8-A 端预审拒绝",
    )

    # ===== 被邀请人识别（路径 C 用，本期 B 路径激活后回填） =====
    invitee_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="被邀请人 sys_user.id"
    )
    invitee_role_in_tenant: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="被邀请人角色 1-管理员 2-员工 3-驾驶员（C2 触发）",
    )

    # ===== C2 转交字段（本期不写入，但表结构预留） =====
    forwarder_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="代转交者 user_id"
    )
    forwarder_tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="C2 场景被邀请人选择转交所在的租户 tenant_code"
    )

    # ===== 接受方信息（本期 B 路径激活后回填） =====
    accepted_tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="最终建立互联时的租户编码"
    )
    accepted_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="最终接受邀请的 user_id"
    )
    accepted_role: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="最终接受方在所选租户中的角色 1-管理员 2-员工",
    )

    # ===== C3 A 端预审字段（本期不读写，但表结构预留） =====
    target_match: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="0-完全匹配 1-相近 2-不匹配（C3 触发）",
    )
    pending_a_review: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="A 端预审待确认 1-是 0-否",
    )
    a_review_decision: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="A 端预审决策：0-未决策 1-同意 2-拒绝",
    )
    a_review_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="进行预审的 A 端操作员 user_id"
    )

    revoked_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="撤回/拒绝/解绑的原因"
    )
