"""
承运商邀请流水 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CarrierInviteRequest(BaseModel):
    """触发邀请请求体（本期渠道固定为 link，操作员手动转发）"""
    channel: str = Field(default="link", description="link（本期仅支持）")
    remark: Optional[str] = None


class CarrierInviteResponse(BaseModel):
    """触发邀请响应"""
    carrierId: int
    inviteId: int
    inviteCode: str
    inviteUrl: str = Field(
        default="",
        description="可直接复制转发的邀请落地页 URL；fast-path 直接互联时为空字符串",
    )
    inviteStatus: int = Field(description="biz_carrier.invite_status")
    invitePath: str = Field(description="B / fast")
    expiresAt: Optional[datetime] = Field(
        default=None,
        description="路径 B 链接式邀请的过期时间；fast-path 直连互联时为 None",
    )
    userExisted: bool = Field(
        description="True 表示该手机号已是 sys_user（fast-path 时也是 True）"
    )
    linkedTenantCode: Optional[str] = Field(
        default=None,
        description="fast-path 直连互联时返回 B 的租户编码；路径 B 链接式时为 None",
    )
    fastLinked: bool = Field(
        default=False,
        description="True 表示已通过 fast-path 直接建立互联，无需对方确认",
    )


class CarrierInvitePhoneCheckOut(BaseModel):
    """邀请前查注册状态响应：操作员在弹框打开时即可看到对方在平台的状态。"""
    phone: str
    registered: bool = Field(description="该手机号是否已在平台注册账号（sys_user）")
    userRealName: Optional[str] = Field(
        default=None,
        description="已注册时返回该 user 的真实姓名（可能为空）",
    )
    tenantCode: Optional[str] = Field(
        default=None,
        description="已注册时返回其当前所属（任一启用中）的租户编码",
    )
    tenantName: Optional[str] = Field(
        default=None,
        description="已注册时返回其当前所属租户名称",
    )
    tenantVersionCode: Optional[str] = Field(
        default=None,
        description="对方租户当前生效的版本编码（lite/basic/...）；判断 fast-path 用",
    )
    canFastLink: bool = Field(
        default=False,
        description="True 表示对方是 lite 租户，可走 fast-path 直接建立互联（无需短信/链接确认）",
    )
    adminName: Optional[str] = Field(
        default=None,
        description="该租户的一名管理员姓名（用户类型=1）",
    )
    adminPhoneMasked: Optional[str] = Field(
        default=None,
        description="该管理员手机号的脱敏形式（如 138****1234）",
    )


class CarrierRevokeRequest(BaseModel):
    reason: Optional[str] = None


class CarrierInvitationOut(BaseModel):
    """邀请流水详情输出"""
    id: int
    carrierId: int
    inviteCode: str
    invitePhone: str
    expectedCarrierName: str
    inviteChannel: str
    invitePath: str
    status: int
    expiresAt: datetime
    invitedAt: datetime
    inviteeUserId: Optional[int] = None
    forwarderUserId: Optional[int] = None
    forwarderTenantCode: Optional[str] = None
    acceptedTenantCode: Optional[str] = None
    acceptedUserId: Optional[int] = None
    acceptedRole: Optional[int] = None
    targetMatch: Optional[int] = None
    pendingAReview: int = 0
    aReviewDecision: Optional[int] = None
    revokedReason: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "CarrierInvitationOut":
        return cls(
            id=m.id,
            carrierId=m.carrier_id,
            inviteCode=m.invite_code,
            invitePhone=m.invite_phone,
            expectedCarrierName=m.expected_carrier_name,
            inviteChannel=m.invite_channel,
            invitePath=m.invite_path,
            status=m.status,
            expiresAt=m.expires_at,
            invitedAt=m.created_at,
            inviteeUserId=m.invitee_user_id,
            forwarderUserId=m.forwarder_user_id,
            forwarderTenantCode=m.forwarder_tenant_code,
            acceptedTenantCode=m.accepted_tenant_code,
            acceptedUserId=m.accepted_user_id,
            acceptedRole=m.accepted_role,
            targetMatch=m.target_match,
            pendingAReview=m.pending_a_review,
            aReviewDecision=m.a_review_decision,
            revokedReason=m.revoked_reason,
        )
