"""
承运商邀请索引中转表（平台库）
B 端用户/管理员查询"我或我所在企业是否有待处理邀请"时的加速表
本期 Phase B 仅由 CarrierInviteService 写入，B 端反查接口不实现
"""

from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class CarrierInvitationInbox(PlatformModelBase):
    """承运商邀请索引中转表"""
    __tablename__ = "sys_carrier_invitation_inbox"
    __table_args__ = (
        UniqueConstraint("invite_code", name="uk_invite_code"),
        Index("idx_invite_phone", "invite_phone"),
        Index("idx_invitee_user_id", "invitee_user_id"),
        Index("idx_forwarder_tenant_status", "forwarder_tenant_code", "status"),
        Index("idx_status_expires", "status", "expires_at"),
        {"comment": "承运商邀请索引中转表（被邀请方反查加速）"},
    )

    invite_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="同 biz_carrier_invitation.invite_code"
    )
    source_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="A 的 tenant_code"
    )
    source_carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="A.biz_carrier.id"
    )
    source_carrier_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="A 录入的承运商名"
    )
    source_tenant_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="A 的企业名"
    )
    invite_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="被邀请手机号"
    )
    invitee_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="invitee sys_user.id（路径 C 写入；路径 B 创建租户后回填）",
    )
    invite_path: Mapped[str] = mapped_column(
        String(8), nullable=False, comment="B / C1 / C2 / C3"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="镜像 biz_carrier_invitation.status",
    )
    forwarder_tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="C2 转交所选租户"
    )
    forwarder_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="C2 转交者 user_id"
    )
    target_admin_tenants: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="C2 待管理员审核的目标租户列表（冗余加速 admin 查询）"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="失效时间"
    )
