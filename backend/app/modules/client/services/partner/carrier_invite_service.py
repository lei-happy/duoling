"""
承运商邀请服务（路径 B 全链路）
本期 Phase B 仅实现：
  - check_phone(phone)：弹框打开时按手机号查询平台注册状态
  - invite(carrier_id)：A 端触发邀请，校验手机号未注册 → 写 invitation + inbox，
                        生成可复制的邀请链接（不再依赖短信网关）
  - revoke_invite(carrier_id)：撤回邀请
  - list_invitations(carrier_id)：邀请历史
  - get_info_by_code(invite_code)：着陆页拉取邀请信息
  - activate(invite_code, ...)：调 TenantService.create_tenant 自动开 lite，回写 link / inbox / 源 carrier

C1/C2/C3 路径与 B 端反查接口不在本期范围。
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.common.exceptions import BizException
from app.core.config import get_settings
from app.core.database import db_manager
from app.core.security import (
    TokenData, create_access_token, create_refresh_token,
)
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.partner.carrier_invitation import CarrierInvitation
from app.modules.client.schemas.partner.carrier_invitation import (
    CarrierInviteRequest, CarrierInviteResponse, CarrierRevokeRequest,
    CarrierInvitePhoneCheckOut,
)
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.console.models.system.carrier_link import CarrierLink
from app.modules.console.models.system.carrier_invitation_inbox import (
    CarrierInvitationInbox,
)
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.tenant.tenant_product import TenantProduct
from app.modules.console.schemas.tenant.tenant import TenantCreate
from app.modules.console.services.tenant.tenant_service import TenantService
from app.modules.open.schemas.carrier_invite import (
    CarrierInviteInfoOut, CarrierInviteActivateRequest,
    CarrierInviteActivateResponse,
)
from app.modules.open.services.sms_service import (
    SmsService, PURPOSE_TENANT_REGISTER,
)


_INVITE_TTL_DAYS = 7
_INVITE_PATH_B = "B"


class CarrierInviteService:

    # ----------------- helpers -----------------

    @staticmethod
    def _gen_invite_code() -> str:
        return secrets.token_urlsafe(16).replace("-", "").replace("_", "")[:24]

    @staticmethod
    def _gen_invite_token() -> Tuple[str, str]:
        """返回 (raw_token, hashed_token)"""
        raw = secrets.token_urlsafe(24)
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return raw, h

    @staticmethod
    def _mask_phone(phone: str) -> str:
        if not phone or len(phone) < 7:
            return phone
        return phone[:3] + "****" + phone[-4:]

    @staticmethod
    def _build_invite_url(invite_code: str) -> str:
        """根据 settings.FRONTEND_BASE_URL 拼接落地页绝对地址。

        - 形如 `http://192.168.1.117:5174/invite-landing/{code}`
        - 自动剥离 base 末尾多余斜杠，确保只有一个 `/`
        """
        base = (get_settings().FRONTEND_BASE_URL or "").rstrip("/")
        return f"{base}/invite-landing/{invite_code}"

    @staticmethod
    async def _check_phone_registered_in_platform(
        platform_db: AsyncSession, phone: str
    ) -> Tuple[bool, Optional[User]]:
        """是否已是 sys_user。本期路径 B 仅未注册手机号才走"""
        r = await platform_db.execute(
            select(User).where(User.phone == phone, User.is_deleted == 0)
        )
        u = r.scalar_one_or_none()
        if not u:
            return False, None
        return True, u

    @staticmethod
    async def _log_invite_link_placeholder(
        carrier_name: str, source_tenant_name: str,
        phone: str, invite_code: str, invite_url: str,
    ) -> str:
        """生成留痕文案（写邀请记录的 sms_content 字段 + 服务端日志）。

        本期不再走短信，链接由 A 端操作员通过微信等私域渠道转发，
        日志中保留可复制 URL 仅用于开发/测试期排查。
        """
        text = (
            f"【智途】{source_tenant_name} 邀请您（{carrier_name}）加入承运商互联，"
            f"点击 {invite_url} 激活，{_INVITE_TTL_DAYS}天内有效，请勿泄露。"
        )
        logger.info(
            f"[CarrierInvite][LINK_GENERATED] phone={phone} url={invite_url}"
        )
        return text

    # ----------------- 弹框打开：查注册状态 -----------------

    @staticmethod
    async def check_phone(
        platform_db: AsyncSession, phone: str
    ) -> CarrierInvitePhoneCheckOut:
        """按手机号查平台注册状态。

        - 未注册：registered=False，前端可继续走路径 B 生成邀请链接。
        - 已注册：返回所属租户名 + 该租户管理员姓名/脱敏手机号（取 user_type=1 的最早一条），
                  前端提示操作员"请联系对方管理员接受邀请"，并禁用"生成邀请链接"按钮。
        """
        if not phone:
            raise BizException("手机号不能为空")

        existed, user = await CarrierInviteService._check_phone_registered_in_platform(
            platform_db, phone
        )
        if not existed or user is None:
            return CarrierInvitePhoneCheckOut(
                phone=phone,
                registered=False,
            )

        # 找用户当前所属的（任一）正常租户。同手机号被多租户共享时取最早绑定的一条
        rt = await platform_db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user.id,
                UserTenant.is_deleted == 0,
                UserTenant.status == 1,
            ).order_by(UserTenant.id.asc()).limit(1)
        )
        ut = rt.scalar_one_or_none()
        if not ut:
            # 已注册但未绑定任何启用中的企业，等同于"无可联系管理员"
            return CarrierInvitePhoneCheckOut(
                phone=phone,
                registered=True,
                userRealName=user.real_name,
            )

        rti = await platform_db.execute(
            select(Tenant).where(
                Tenant.tenant_code == ut.tenant_code,
                Tenant.is_deleted == 0,
            )
        )
        tenant = rti.scalar_one_or_none()
        tenant_name = tenant.tenant_name if tenant else None

        # 取对方租户当前生效的产品版本（用于判断是否 fast-path 直连）
        tenant_version_code = await CarrierInviteService._get_tenant_active_version_code(
            platform_db, ut.tenant_code
        )
        can_fast_link = tenant_version_code == "lite"

        # 取该租户的管理员（user_type=1），优先返回与当前手机号不同的人，便于操作员联系
        admin_user: Optional[User] = None
        ra = await platform_db.execute(
            select(User)
            .join(UserTenant, UserTenant.user_id == User.id)
            .where(
                UserTenant.tenant_code == ut.tenant_code,
                UserTenant.user_type == 1,
                UserTenant.status == 1,
                UserTenant.is_deleted == 0,
                User.is_deleted == 0,
                User.status == 1,
            ).order_by(UserTenant.id.asc())
        )
        admin_candidates = list(ra.scalars().all())
        for cand in admin_candidates:
            if cand.phone != phone:
                admin_user = cand
                break
        if admin_user is None and admin_candidates:
            admin_user = admin_candidates[0]

        return CarrierInvitePhoneCheckOut(
            phone=phone,
            registered=True,
            userRealName=user.real_name,
            tenantCode=ut.tenant_code,
            tenantName=tenant_name,
            tenantVersionCode=tenant_version_code,
            canFastLink=can_fast_link,
            adminName=admin_user.real_name if admin_user else None,
            adminPhoneMasked=(
                CarrierInviteService._mask_phone(admin_user.phone)
                if admin_user else None
            ),
        )

    @staticmethod
    async def _get_tenant_active_version_code(
        platform_db: AsyncSession, tenant_code: str
    ) -> Optional[str]:
        """取租户当前生效的产品版本编码（取 sort_order 最小的一条，等同于"最低档"，
        因为多版本叠加时通常只关心是否 lite）。

        实际项目中一个租户通常只有一个 active 的 TenantProduct；这里多版本兜底也安全。
        """
        from sqlalchemy import or_
        now = datetime.now()
        r = await platform_db.execute(
            select(TenantProduct.version_code).where(
                TenantProduct.tenant_code == tenant_code,
                TenantProduct.is_deleted == 0,
                TenantProduct.status == 1,
                or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > now),
            ).order_by(TenantProduct.id.asc()).limit(1)
        )
        return r.scalar_one_or_none()

    # ----------------- fast-path：对方已是 lite 租户时直接互联 -----------------

    @staticmethod
    async def _find_user_lite_tenant(
        platform_db: AsyncSession, user_id: int
    ) -> Optional[Tenant]:
        """如果该用户当前正绑定一个 lite 租户，则返回该租户对象；否则 None。

        多租户用户取第一个 active 的；若该 active 的 version 非 lite 则视为不可走 fast-path。
        """
        rt = await platform_db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user_id,
                UserTenant.is_deleted == 0,
                UserTenant.status == 1,
            ).order_by(UserTenant.id.asc())
        )
        for ut in rt.scalars().all():
            ver = await CarrierInviteService._get_tenant_active_version_code(
                platform_db, ut.tenant_code
            )
            if ver == "lite":
                t_r = await platform_db.execute(
                    select(Tenant).where(
                        Tenant.tenant_code == ut.tenant_code,
                        Tenant.is_deleted == 0,
                    )
                )
                t = t_r.scalar_one_or_none()
                if t is not None:
                    return t
            # 否则继续看下一条 user_tenant；多数情况下只有 1 条
        return None

    @staticmethod
    async def _fast_link_existing_lite(
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        source_tenant_code: str,
        operator_user_id: Optional[int],
        carrier: Carrier,
        target_user: User,
        target_tenant: Tenant,
    ) -> CarrierInviteResponse:
        """fast-path 直接建立互联（对方已是 lite 租户）。

        - 写一条 invitation，渠道 fast、状态 3（已激活），完整记录可追溯
        - 写一条 inbox，状态 3（已激活）
        - 写一条 link（A.source_tenant_code + A.carrier.id → B.tenant_code）
        - 更新 A.carrier：linked_tenant_code=B、invite_status=2、activated_at=now
        - 不发链接、不写 token
        - 与已有 (source_tenant_code, source_carrier_id) UNIQUE 兼容（每个 A 端 carrier 只能 link 一次）
        """
        now = datetime.now()
        invite_code = CarrierInviteService._gen_invite_code()

        # 取源租户名（冗余写入 link / inbox）
        rt = await platform_db.execute(
            select(Tenant).where(
                Tenant.tenant_code == source_tenant_code,
                Tenant.is_deleted == 0,
            )
        )
        source_tenant = rt.scalar_one_or_none()
        source_tenant_name = (
            source_tenant.tenant_name if source_tenant else source_tenant_code
        )

        # 1. 写 invitation：channel=fast、status=3 已激活
        #    invite_token 列 NOT NULL，fast-path 没有真实 token，写占位串便于审计识别
        invitation = CarrierInvitation(
            carrier_id=carrier.id,
            invite_code=invite_code,
            invite_phone=carrier.contact_phone,
            expected_carrier_name=carrier.carrier_name,
            invite_channel="fast",
            sms_content=(
                f"[CarrierInvite][FAST_LINK] {source_tenant_name} 直连 lite 租户 "
                f"{target_tenant.tenant_code}({target_tenant.tenant_name})"
            ),
            invite_token=f"FAST_LINK_NO_TOKEN_{invite_code}",
            expires_at=now,
            invite_path="fast",
            status=3,  # 已激活
            pending_a_review=0,
            invitee_user_id=target_user.id,
            accepted_tenant_code=target_tenant.tenant_code,
            accepted_user_id=target_user.id,
            accepted_role=1,
        )
        tenant_db.add(invitation)

        # 2. 更新 carrier：直接进入"已激活"
        carrier.invite_status = 2
        carrier.invite_user_id = operator_user_id
        carrier.invited_at = now
        carrier.activated_at = now
        carrier.linked_tenant_code = target_tenant.tenant_code
        await tenant_db.flush()

        # 3. 写 inbox：status=3 已激活
        inbox = CarrierInvitationInbox(
            invite_code=invite_code,
            source_tenant_code=source_tenant_code,
            source_carrier_id=carrier.id,
            source_carrier_name=carrier.carrier_name,
            source_tenant_name=source_tenant_name,
            invite_phone=carrier.contact_phone,
            invitee_user_id=target_user.id,
            invite_path="fast",
            status=3,
            expires_at=now,
        )
        platform_db.add(inbox)

        # 4. 写 link
        link = CarrierLink(
            source_tenant_code=source_tenant_code,
            source_carrier_id=carrier.id,
            source_carrier_name=carrier.carrier_name,
            source_tenant_name=source_tenant_name,
            linked_tenant_code=target_tenant.tenant_code,
            link_status=1,
            cooperation_start=now.date(),
        )
        platform_db.add(link)
        await platform_db.flush()

        logger.info(
            f"[CarrierInvite][FAST_LINK_OK] source={source_tenant_code} "
            f"carrier_id={carrier.id} → linked={target_tenant.tenant_code}"
        )

        return CarrierInviteResponse(
            carrierId=carrier.id,
            inviteId=invitation.id,
            inviteCode=invite_code,
            inviteUrl="",
            inviteStatus=carrier.invite_status,
            invitePath="fast",
            expiresAt=None,
            userExisted=True,
            linkedTenantCode=target_tenant.tenant_code,
            fastLinked=True,
        )

    # ----------------- A 端触发 / 撤回 / 查询 -----------------

    @staticmethod
    async def list_invitations(
        tenant_db: AsyncSession, carrier_id: int
    ) -> List[CarrierInvitation]:
        r = await tenant_db.execute(
            select(CarrierInvitation).where(
                CarrierInvitation.carrier_id == carrier_id,
                CarrierInvitation.is_deleted == 0,
            ).order_by(CarrierInvitation.created_at.desc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def invite(
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        source_tenant_code: str,
        operator_user_id: Optional[int],
        carrier_id: int,
        data: CarrierInviteRequest,
    ) -> CarrierInviteResponse:
        # 1. 取承运商
        rc = await tenant_db.execute(
            select(Carrier).where(
                Carrier.id == carrier_id,
                Carrier.is_deleted == 0,
            )
        )
        carrier = rc.scalar_one_or_none()
        if not carrier:
            raise BizException("承运商不存在")
        if carrier.linked_tenant_code:
            raise BizException("该承运商已激活互联，无需重复邀请")
        if carrier.invite_status == 1:
            raise BizException("已有邀请进行中，请先撤回")

        # 2. 路径分支：B（链接式邀请）/ fast（对方已是 lite 直连）/ 其他真实租户用户拒绝
        user_existed, existing_user = await CarrierInviteService._check_phone_registered_in_platform(
            platform_db, carrier.contact_phone
        )
        if user_existed and existing_user is not None:
            target_lite_tenant = await CarrierInviteService._find_user_lite_tenant(
                platform_db, existing_user.id
            )
            if target_lite_tenant is not None:
                # fast-path：对方是 lite 租户（很可能由其他 A 通过承运商邀请激活），
                # 本 A 直接建立互联，不再发链接、不再让对方确认。
                return await CarrierInviteService._fast_link_existing_lite(
                    tenant_db=tenant_db,
                    platform_db=platform_db,
                    source_tenant_code=source_tenant_code,
                    operator_user_id=operator_user_id,
                    carrier=carrier,
                    target_user=existing_user,
                    target_tenant=target_lite_tenant,
                )
            # 已注册但不是 lite 租户用户：仍需走 C 路径
            raise BizException(
                "该手机号已在其他企业开户，需走 C1/C2/C3 路径，本期暂未开放；"
                "请联系对方管理员在系统内接受邀请"
            )

        # 3. 取源租户名（写入 inbox / link 时冗余）
        rt = await platform_db.execute(
            select(Tenant).where(
                Tenant.tenant_code == source_tenant_code,
                Tenant.is_deleted == 0,
            )
        )
        source_tenant = rt.scalar_one_or_none()
        source_tenant_name = source_tenant.tenant_name if source_tenant else source_tenant_code

        # 4. 生成邀请码、邀请链接与 token，写 invitation
        invite_code = CarrierInviteService._gen_invite_code()
        _raw_token, hashed_token = CarrierInviteService._gen_invite_token()
        expires_at = datetime.now() + timedelta(days=_INVITE_TTL_DAYS)
        invite_url = CarrierInviteService._build_invite_url(invite_code)
        invite_content = await CarrierInviteService._log_invite_link_placeholder(
            carrier.carrier_name, source_tenant_name,
            carrier.contact_phone, invite_code, invite_url,
        )

        # 邀请渠道本期固定为 link（操作员通过微信等私域渠道转发链接）
        invitation = CarrierInvitation(
            carrier_id=carrier.id,
            invite_code=invite_code,
            invite_phone=carrier.contact_phone,
            expected_carrier_name=carrier.carrier_name,
            invite_channel="link",
            sms_content=invite_content,
            invite_token=hashed_token,
            expires_at=expires_at,
            invite_path=_INVITE_PATH_B,
            status=1,  # 已发送（视为"已生成可分发链接"）
            pending_a_review=0,
        )
        tenant_db.add(invitation)

        # 5. 同步 carrier 主体邀请状态
        carrier.invite_status = 1
        carrier.invite_user_id = operator_user_id
        carrier.invited_at = datetime.now()

        await tenant_db.flush()

        # 6. 写平台库 inbox（路径 B 此时被邀请人尚未注册，invitee_user_id=None）
        inbox = CarrierInvitationInbox(
            invite_code=invite_code,
            source_tenant_code=source_tenant_code,
            source_carrier_id=carrier.id,
            source_carrier_name=carrier.carrier_name,
            source_tenant_name=source_tenant_name,
            invite_phone=carrier.contact_phone,
            invitee_user_id=None,
            invite_path=_INVITE_PATH_B,
            status=1,
            expires_at=expires_at,
        )
        platform_db.add(inbox)
        await platform_db.flush()

        return CarrierInviteResponse(
            carrierId=carrier.id,
            inviteId=invitation.id,
            inviteCode=invite_code,
            inviteUrl=invite_url,
            inviteStatus=carrier.invite_status,
            invitePath=_INVITE_PATH_B,
            expiresAt=expires_at,
            userExisted=False,
            linkedTenantCode=None,
        )

    @staticmethod
    async def revoke_invite(
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        carrier_id: int,
        data: Optional[CarrierRevokeRequest] = None,
    ) -> None:
        rc = await tenant_db.execute(
            select(Carrier).where(
                Carrier.id == carrier_id,
                Carrier.is_deleted == 0,
            )
        )
        carrier = rc.scalar_one_or_none()
        if not carrier:
            raise BizException("承运商不存在")
        if carrier.invite_status not in (1, 4, 7):
            raise BizException("当前没有进行中的邀请，无需撤回")
        if carrier.linked_tenant_code:
            raise BizException("已激活互联的承运商不可撤回邀请，请走解绑")

        # 找最近一条进行中邀请
        ri = await tenant_db.execute(
            select(CarrierInvitation).where(
                CarrierInvitation.carrier_id == carrier.id,
                CarrierInvitation.is_deleted == 0,
                CarrierInvitation.status.in_((1, 2, 7)),
            ).order_by(CarrierInvitation.created_at.desc()).limit(1)
        )
        invitation = ri.scalar_one_or_none()
        reason = (data.reason if data else None) or "A 端操作员撤回"

        if invitation:
            invitation.status = 5  # A 已撤回
            invitation.revoked_reason = reason

            # 同步 inbox
            ib_r = await platform_db.execute(
                select(CarrierInvitationInbox).where(
                    CarrierInvitationInbox.invite_code == invitation.invite_code,
                    CarrierInvitationInbox.is_deleted == 0,
                )
            )
            inbox = ib_r.scalar_one_or_none()
            if inbox:
                inbox.status = 5

        # 同步 carrier 主体
        carrier.invite_status = 5  # A 已撤回
        await tenant_db.flush()
        await platform_db.flush()

    # ----------------- 着陆页 / 激活（开放接口） -----------------

    @staticmethod
    async def get_info_by_code(
        platform_db: AsyncSession, invite_code: str
    ) -> CarrierInviteInfoOut:
        """着陆页加载邀请信息（仅查 inbox + sys_user 是否已注册）"""
        r = await platform_db.execute(
            select(CarrierInvitationInbox).where(
                CarrierInvitationInbox.invite_code == invite_code,
                CarrierInvitationInbox.is_deleted == 0,
            )
        )
        inbox = r.scalar_one_or_none()
        if not inbox:
            raise BizException("邀请不存在或已失效")

        expired = (
            datetime.now() > inbox.expires_at
            or inbox.status in (4, 5, 6, 8)
        )
        # 检查手机号当前是否已注册（用户可能在邀请期间注册了别的企业）
        ur = await platform_db.execute(
            select(User.id).where(
                User.phone == inbox.invite_phone,
                User.is_deleted == 0,
            ).limit(1)
        )
        user_existed = ur.scalar_one_or_none() is not None

        return CarrierInviteInfoOut(
            inviteCode=inbox.invite_code,
            sourceTenantName=inbox.source_tenant_name or inbox.source_tenant_code,
            expectedCarrierName=inbox.source_carrier_name,
            invitePhoneMasked=CarrierInviteService._mask_phone(inbox.invite_phone),
            invitePath=inbox.invite_path,
            status=inbox.status,
            expiresAt=inbox.expires_at,
            expired=expired,
            userExisted=user_existed,
        )

    @staticmethod
    async def activate(
        platform_db: AsyncSession,
        data: CarrierInviteActivateRequest,
    ) -> CarrierInviteActivateResponse:
        """
        路径 B 激活：手机号未注册 → 创建 lite 租户 → 回写 invitation/carrier/inbox/link
        激活成功后下发可直接登录的 access_token
        """
        # 1. 校验邀请
        ir = await platform_db.execute(
            select(CarrierInvitationInbox).where(
                CarrierInvitationInbox.invite_code == data.inviteCode,
                CarrierInvitationInbox.is_deleted == 0,
            )
        )
        inbox = ir.scalar_one_or_none()
        if not inbox:
            raise BizException("邀请不存在或已失效")
        if datetime.now() > inbox.expires_at:
            raise BizException("邀请已过期")
        if inbox.status not in (1, 2):
            raise BizException("邀请状态异常，无法激活")
        if inbox.invite_path != _INVITE_PATH_B:
            raise BizException("此邀请属于互联进阶路径，本期暂未开放")
        if inbox.invite_phone != data.contactPhone:
            raise BizException("手机号与邀请记录不一致，请核对")

        # 2. 路径 B 前置：手机号必须未注册
        existed, _u = await CarrierInviteService._check_phone_registered_in_platform(
            platform_db, data.contactPhone
        )
        if existed:
            raise BizException(
                "该手机号已注册账号，需走互联进阶路径（C1/C2/C3），本期暂未开放"
            )

        # 3. 校验短信验证码（路径 B 与官网开企业一致，使用 TENANT_REGISTER=4 通道）
        await SmsService.verify_code(
            platform_db, data.contactPhone, data.smsCode,
            PURPOSE_TENANT_REGISTER, consume=True,
        )

        # 4. 调 TenantService.create_tenant 开通 lite 不限期
        tenant_create = TenantCreate(
            tenantName=data.tenantName,
            shortName=data.shortName,
            contactPerson=data.realName,
            contactPhone=data.contactPhone,
            sourceChannel="carrier_invite",
            referrerCode=inbox.source_tenant_code,
            inviteSourceTenant=inbox.source_tenant_code,
            remark=f"由 {inbox.source_tenant_name or inbox.source_tenant_code} 通过承运商邀请激活",
        )
        new_tenant, _is_existing = await TenantService.create_tenant(
            platform_db, tenant_create,
        )
        # 标记为正常状态（与官网注册逻辑一致）
        new_tenant.status = 1
        await platform_db.flush()

        # 5. 取新建管理员 user
        ur = await platform_db.execute(
            select(User).where(
                User.phone == data.contactPhone,
                User.is_deleted == 0,
            )
        )
        admin_user = ur.scalar_one()

        # 6. 写互联镜像 link
        link = CarrierLink(
            source_tenant_code=inbox.source_tenant_code,
            source_carrier_id=inbox.source_carrier_id,
            source_carrier_name=inbox.source_carrier_name,
            source_tenant_name=inbox.source_tenant_name,
            linked_tenant_code=new_tenant.tenant_code,
            link_status=1,
            cooperation_start=datetime.now().date(),
        )
        platform_db.add(link)

        # 7. 更新 inbox：标记激活、回填 invitee_user_id
        inbox.status = 3
        inbox.invitee_user_id = admin_user.id

        # 8. 回写源 A 端 invitation + carrier
        try:
            async for src_db in db_manager.get_tenant_session(inbox.source_tenant_code):
                inv_r = await src_db.execute(
                    select(CarrierInvitation).where(
                        CarrierInvitation.invite_code == data.inviteCode,
                        CarrierInvitation.is_deleted == 0,
                    )
                )
                invitation = inv_r.scalar_one_or_none()
                if invitation:
                    invitation.status = 3  # 已激活
                    invitation.accepted_tenant_code = new_tenant.tenant_code
                    invitation.accepted_user_id = admin_user.id
                    invitation.accepted_role = 1
                    invitation.invitee_user_id = admin_user.id

                cr = await src_db.execute(
                    select(Carrier).where(
                        Carrier.id == inbox.source_carrier_id,
                        Carrier.is_deleted == 0,
                    )
                )
                carrier = cr.scalar_one_or_none()
                if carrier:
                    carrier.linked_tenant_code = new_tenant.tenant_code
                    carrier.invite_status = 2  # 已激活
                    carrier.activated_at = datetime.now()

                await src_db.commit()
        except Exception as e:
            # 回写失败不影响 B 端 lite 租户创建，记录日志由人工补救
            logger.error(
                f"[CarrierInvite] 激活回写源租户失败 source={inbox.source_tenant_code} "
                f"invite_code={data.inviteCode} err={e}"
            )

        await platform_db.flush()

        # 9. 下发登录 token（绑定到新 lite 租户）
        token_data = TokenData(
            user_id=admin_user.id,
            phone=admin_user.phone,
            user_type=admin_user.user_type,
            tenant_code=new_tenant.tenant_code,
            roles=["tenant_admin"],
        )
        access = create_access_token(token_data)
        refresh = create_refresh_token(token_data)

        return CarrierInviteActivateResponse(
            tenantCode=new_tenant.tenant_code,
            tenantName=new_tenant.tenant_name,
            versionCode="lite",
            accessToken=access,
            refreshToken=refresh,
        )
