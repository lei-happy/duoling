"""发布 / 编辑前的上下文装载（读平台库）

``EcoPublishService.publish`` 与 ``EcoPostManageService`` 都要求调用方**先把
两样东西查好再传进来**：发布人身份（``PublisherContext``）和预检素材里需要
查库的那一半（``PrecheckInput``）。这里把这两件事收在一处。

## 为什么不让各个 API 各自拼

租户端一共有四个入口会跑预检：发布货源、发布运力、编辑、重新上架 / 提交审核。
四处各拼一遍 ``PrecheckInput``，迟早出现「某个入口忘了带敏感词库」——而它的
表现是**那条路径上的敏感词规则静默失效**，不报错、不告警，只有事后被举报时
才会发现。收成一个函数后，忘带的可能性只剩一处。

## 企业名片为什么不在 GET 里懒建

``07`` §4.11 写的是「租户首次访问大厅时按 sys_tenant 自动建一条」，这里改成
**首次发布时才建**：读接口里写库会让大厅列表这个最高频的 GET 变成写事务，
而名片缺失在读路径上已经处处按安全侧兜住了（可见性把缺记录当未认证，
大厅范围把缺记录当未关停）。发布本来就是写请求，在那里建没有额外代价。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.services.ecosystem.content_guard import PrecheckInput
from app.modules.client.services.ecosystem.post_draft import PostDraft
from app.modules.client.services.ecosystem.post_manage_service import OwnerContext
from app.modules.client.services.ecosystem.publish_service import PublisherContext
from app.modules.client.services.ecosystem.visibility import mask_company_name
from app.modules.console.models.ecosystem.constants import PostStatus
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile
from app.modules.console.models.system.sensitive_word import SensitiveWordScope
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.services.system.sensitive_word_service import (
    SensitiveWordService,
)

# 「近 24 小时发布数」与「相似挂牌」的回溯窗口
RECENT_HOURS = 24
SIMILAR_DAYS = 7


@dataclass
class TenantHallContext:
    """租户在服务平台的身份快照

    一次查询取全：名字、认证、大厅能力、免审白名单、注册天数、发布默认偏好。
    发布弹层的默认值和发布链路的门控读的是同一份数据，避免「弹层显示可发布、
    提交时被拒」这种前后不一致。
    """

    tenant_code: str
    tenant_name: str = ""
    masked_name: Optional[str] = None
    license_verified: bool = False
    hall_enabled: bool = True
    disabled_reason: Optional[str] = None
    audit_whitelist: bool = False
    tenant_age_days: Optional[int] = None
    # 发布弹层默认值（来自名片，缺名片时用系统默认）
    default_valid_days: int = 7
    default_visibility_level: int = 2
    default_contact_visibility: int = 3
    default_contact_name: Optional[str] = None
    default_contact_phone: Optional[str] = None
    # 名片是否已建，供发布链路决定要不要补建
    profile_exists: bool = False

    @property
    def display_masked_name(self) -> str:
        return self.masked_name or mask_company_name(self.tenant_name)


class EcoPublishContextService:
    """发布 / 编辑上下文"""

    # ------------------------------------------------------------------
    # 身份快照
    # ------------------------------------------------------------------

    @staticmethod
    async def load_tenant(
        platform_db: AsyncSession,
        tenant_code: str,
        *,
        now: Optional[datetime] = None,
    ) -> TenantHallContext:
        """装载租户在服务平台的身份快照

        名片与信誉都是懒加载表，查不到记录时一律**取安全侧默认**：未认证、
        非白名单。反过来（缺记录就当已认证）会让一个还没被运营碰过的新租户
        直接拿到认证层的可见范围。
        """
        now = now or datetime.now()

        row = (
            await platform_db.execute(
                select(
                    Tenant.tenant_name,
                    Tenant.created_at,
                    SysEcoTenantProfile.id.label("profile_id"),
                    SysEcoTenantProfile.masked_name,
                    SysEcoTenantProfile.license_verified,
                    SysEcoTenantProfile.hall_enabled,
                    SysEcoTenantProfile.disabled_reason,
                    SysEcoTenantProfile.disabled_until,
                    SysEcoTenantProfile.default_valid_days,
                    SysEcoTenantProfile.default_visibility_level,
                    SysEcoTenantProfile.default_contact_visibility,
                    SysEcoTenantProfile.contact_name,
                    SysEcoTenantProfile.contact_phone,
                    SysEcoTenantCredit.audit_whitelist,
                )
                .select_from(Tenant)
                .outerjoin(
                    SysEcoTenantProfile,
                    (SysEcoTenantProfile.tenant_code == Tenant.tenant_code)
                    & (SysEcoTenantProfile.is_deleted == 0),
                )
                .outerjoin(
                    SysEcoTenantCredit,
                    (SysEcoTenantCredit.tenant_code == Tenant.tenant_code)
                    & (SysEcoTenantCredit.is_deleted == 0),
                )
                .where(Tenant.tenant_code == tenant_code, Tenant.is_deleted == 0)
            )
        ).first()

        if row is None:
            # 租户查不到时不抛异常：调用方是已登录会话，走到这里说明数据异常，
            # 按「无名字、未认证」继续，后续门控自然会挡住发布
            return TenantHallContext(tenant_code=tenant_code)

        ctx = TenantHallContext(
            tenant_code=tenant_code,
            tenant_name=row.tenant_name or "",
            masked_name=row.masked_name,
            license_verified=int(row.license_verified or 0) == 1,
            audit_whitelist=int(row.audit_whitelist or 0) == 1,
            profile_exists=row.profile_id is not None,
            default_valid_days=int(row.default_valid_days or 7),
            default_visibility_level=int(row.default_visibility_level or 2),
            default_contact_visibility=int(row.default_contact_visibility or 3),
            default_contact_name=row.contact_name,
            default_contact_phone=row.contact_phone,
        )

        # 关停到期即自动恢复，不等运营手动点开——否则一次「停 7 天」的处置
        # 会因为没人记得回来解封而变成永久封停
        hall_enabled = row.profile_id is None or int(row.hall_enabled or 0) == 1
        if not hall_enabled and row.disabled_until and row.disabled_until <= now:
            hall_enabled = True
        ctx.hall_enabled = hall_enabled
        ctx.disabled_reason = None if hall_enabled else row.disabled_reason

        if row.created_at:
            ctx.tenant_age_days = max(0, (now - row.created_at).days)

        return ctx

    @staticmethod
    async def ensure_profile(
        platform_db: AsyncSession, ctx: TenantHallContext
    ) -> None:
        """首次发布时补建企业名片

        只在发布链路调用（写请求）。已存在时什么都不做。
        """
        if ctx.profile_exists:
            return
        platform_db.add(
            SysEcoTenantProfile(
                tenant_code=ctx.tenant_code,
                display_name=ctx.tenant_name or None,
                masked_name=ctx.display_masked_name,
            )
        )
        await platform_db.flush()
        ctx.profile_exists = True

    # ------------------------------------------------------------------
    # 转成各 Service 需要的入参
    # ------------------------------------------------------------------

    @staticmethod
    def publisher(
        ctx: TenantHallContext,
        *,
        user_id: Optional[int] = None,
        user_name: Optional[str] = None,
    ) -> PublisherContext:
        return PublisherContext(
            tenant_code=ctx.tenant_code,
            tenant_name=ctx.tenant_name,
            user_id=user_id,
            user_name=user_name,
            masked_name=ctx.display_masked_name,
            audit_whitelist=ctx.audit_whitelist,
            hall_enabled=ctx.hall_enabled,
            disabled_reason=ctx.disabled_reason,
        )

    @staticmethod
    def owner(
        ctx: TenantHallContext,
        *,
        user_id: Optional[int] = None,
        user_name: Optional[str] = None,
    ) -> OwnerContext:
        return OwnerContext(
            tenant_code=ctx.tenant_code,
            user_id=user_id,
            user_name=user_name,
            audit_whitelist=ctx.audit_whitelist,
        )

    # ------------------------------------------------------------------
    # 预检素材里需要查库的部分
    # ------------------------------------------------------------------

    @staticmethod
    async def load_precheck(
        platform_db: AsyncSession,
        *,
        ctx: TenantHallContext,
        draft: Optional[PostDraft] = None,
        exclude_post_id: Optional[int] = None,
        now: Optional[datetime] = None,
    ) -> PrecheckInput:
        """装载预检输入

        线路、时间、文本、证照这些**以草稿为准**，由 ``run_draft_precheck``
        自己覆盖写入（见 ``post_draft`` 模块注释），这里只负责查库的部分。

        Args:
            draft: 用于相似挂牌判定；不传则跳过该项（仍会带敏感词库等其他素材）
            exclude_post_id: 编辑场景要排除自己，否则每次编辑都会把自己判成
                「与近 7 天某条挂牌高度相似」
        """
        now = now or datetime.now()

        rules = await SensitiveWordService.get_rules(
            platform_db, SensitiveWordScope.ECOSYSTEM
        )

        posts_last_24h, total_posts = await EcoPublishContextService._post_counts(
            platform_db, ctx.tenant_code, now=now, exclude_post_id=exclude_post_id
        )

        similar_post_no = None
        if draft is not None:
            similar_post_no = await EcoPublishContextService._find_similar(
                platform_db,
                tenant_code=ctx.tenant_code,
                draft=draft,
                now=now,
                exclude_post_id=exclude_post_id,
            )

        return PrecheckInput(
            sensitive_words=rules,
            now=now,
            posts_last_24h=posts_last_24h,
            tenant_age_days=ctx.tenant_age_days,
            is_first_post=total_posts == 0,
            similar_post_no=similar_post_no,
            # 同线路历史均价的基线一期没有数据，报价异常规则先关闭（04 §2.3）
            price_ratio_to_baseline=None,
        )

    @staticmethod
    async def _post_counts(
        platform_db: AsyncSession,
        tenant_code: str,
        *,
        now: datetime,
        exclude_post_id: Optional[int] = None,
    ) -> tuple[int, int]:
        """(近 24 小时发布数, 累计发布数)

        一条 SQL 拿两个数：两者都只是给预检做判断的计数，分两次查会在高频的
        发布接口上白白多一个来回。
        """
        recent_at = now - timedelta(hours=RECENT_HOURS)
        stmt = select(
            func.count(),
            func.sum(case((SysEcoPost.created_at >= recent_at, 1), else_=0)),
        ).where(
            SysEcoPost.owner_tenant_code == tenant_code,
            SysEcoPost.is_deleted == 0,
        )
        if exclude_post_id is not None:
            stmt = stmt.where(SysEcoPost.id != int(exclude_post_id))

        row = (await platform_db.execute(stmt)).first()
        if row is None:
            return 0, 0
        total = int(row[0] or 0)
        recent = int(row[1] or 0)
        return recent, total

    @staticmethod
    async def _find_similar(
        platform_db: AsyncSession,
        *,
        tenant_code: str,
        draft: PostDraft,
        now: datetime,
        exclude_post_id: Optional[int] = None,
    ) -> Optional[str]:
        """近 7 天内是否已有一条高度相似的挂牌

        相似的判据是**同线路 + 同装车日 + 同台数**三条同时成立，而不只是同线路。
        专线公司天天发同一条线路是常态，只比线路会把这类租户的每一条挂牌都标成
        可疑——标记一旦泛滥，审核员就会开始无视它，等于把这条规则关掉了。
        """
        if not draft.from_province:
            return None

        since = now - timedelta(days=SIMILAR_DAYS)
        stmt = (
            select(SysEcoPost.post_no)
            .where(
                SysEcoPost.owner_tenant_code == tenant_code,
                SysEcoPost.post_type == int(draft.post_type),
                SysEcoPost.is_deleted == 0,
                SysEcoPost.status.notin_(
                    [PostStatus.CANCELLED, PostStatus.REJECTED]
                ),
                SysEcoPost.created_at >= since,
                SysEcoPost.from_province == draft.from_province,
                _eq_or_null(SysEcoPost.from_city, draft.from_city),
                _eq_or_null(SysEcoPost.to_province, draft.to_province),
                _eq_or_null(SysEcoPost.to_city, draft.to_city),
            )
            .order_by(SysEcoPost.created_at.desc())
            .limit(1)
        )
        if exclude_post_id is not None:
            stmt = stmt.where(SysEcoPost.id != int(exclude_post_id))
        if draft.total_quantity is not None:
            stmt = stmt.where(SysEcoPost.total_quantity == int(draft.total_quantity))
        if draft.window_start is not None:
            stmt = stmt.where(
                func.date(SysEcoPost.window_start) == draft.window_start.date()
            )

        return (await platform_db.execute(stmt)).scalars().first()


def _eq_or_null(column, value):
    """值为空时要求列也为空，否则等值匹配

    相似判定里「两条都没填目的地」应当算同一条线路，所以空值走 IS NULL
    而不是被忽略——忽略掉的话，一条没填目的地的挂牌会与所有同起点的挂牌相似。
    """
    if value is None:
        return column.is_(None)
    return column == value
