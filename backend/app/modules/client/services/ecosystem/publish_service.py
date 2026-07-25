"""挂牌发布：平台库 + 租户库双写

## 为什么必须双写

大厅列表要跨租户分页排序，只能放平台库；任务单列表要显示「已发布到大厅」角标，
不能每行都跨库查。于是挂牌主体落 ``sys_eco_post``，租户侧留一条
``biz_eco_post_ref`` 做镜像。

## 写入顺序与它的代价

**必须平台库先写**：``biz_eco_post_ref.post_id`` 依赖平台库自增出来的 ID，
顺序反不过来。代价是存在一个窗口——平台库已提交、租户库提交失败。
两个 Session 由 FastAPI 依赖分别 commit，不是一个事务，无法消除这个窗口。

因此**查重的权威来源是平台库，不是租户库的 ref**（索引
``idx_eco_post_source`` 就是为此而建）。这样即使 ref 丢了，最坏结果只是
任务单上少一个角标，不会让同一张任务单被重复挂到大厅。ref 可以由巡检 Worker
从 ``sys_eco_post`` 反向重建，而重复挂牌一旦发出去就收不回来了。

## 幂等

同一源单在平台库存在非终态挂牌时直接拒绝，并把已有编号告诉用户，
而不是抛一个「重复发布」了事——用户下一步想做的是去看那条挂牌。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/01.架构与撮合内核设计.md §2.2
          doc/02.需求文档/02.企业端/13.服务平台/07.数据库设计.md §3.6
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.ecosystem.post_ref import BizEcoPostRef
from app.modules.client.services.ecosystem.content_guard import (
    PrecheckInput,
    PrecheckResult,
)
from app.modules.client.services.ecosystem.post_draft import (
    PostDraft,
    run_draft_precheck,
)
from app.modules.client.services.ecosystem.visibility import mask_company_name
from app.modules.console.models.ecosystem.capacity_post import SysEcoCapacityPost
from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost
from app.modules.console.models.ecosystem.constants import (
    AuditStatus,
    OperatorType,
    PostAuditAction,
    PostStatus,
    PostType,
    SourceType,
)
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest
from app.modules.console.services.ecosystem.eco_number_service import EcoNumberService

# 挂牌编号唯一索引冲突后的重试次数。Redis 正常时几乎不会走到，
# 留 3 次是为了覆盖 Redis 丢键后水位重建的那一两次撞车。
MAX_POST_NO_RETRY = 3

# 扩展表按类型分发，避免内核里出现 if post_type
_EXT_MODELS = {
    PostType.CARGO: SysEcoCargoPost,
    PostType.CAPACITY: SysEcoCapacityPost,
}

_HALL_NAMES = {PostType.CARGO: "货源大厅", PostType.CAPACITY: "运力大厅"}


@dataclass
class PublisherContext:
    """发布人身份与租户快照"""

    tenant_code: str
    tenant_name: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    masked_name: Optional[str] = None
    # 免审白名单（sys_eco_tenant_credit.audit_whitelist）
    audit_whitelist: bool = False
    # 大厅能力是否开启（运营可关停违规租户）
    hall_enabled: bool = True
    disabled_reason: Optional[str] = None


@dataclass
class PublishResult:
    post_id: int
    post_no: str
    status: int
    audit_status: int
    # 是否免审直通上架
    auto_listed: bool
    suspicious_flags: List[str]
    hit_words: List[str]
    # 租户侧镜像是否落库成功。False 表示角标暂时不显示，待巡检补偿
    ref_synced: bool
    message: str


class EcoPublishService:
    """挂牌发布"""

    @staticmethod
    async def publish(
        *,
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        draft: PostDraft,
        publisher: PublisherContext,
        precheck: Optional[PrecheckInput] = None,
        now: Optional[datetime] = None,
    ) -> PublishResult:
        """发布一条挂牌

        Args:
            draft: 已由 Builder 填好的草稿
            precheck: 预检素材（敏感词库、近 24h 发布数等），由调用方查库准备。
                传 None 表示跳过预检——**只有运营侧补录场景才允许**。
        """
        now = now or datetime.now()

        EcoPublishService._assert_hall_enabled(publisher)
        EcoPublishService._assert_draft_complete(draft)

        existing = await EcoPublishService._find_active_post(
            platform_db, publisher.tenant_code, draft
        )
        if existing is not None:
            raise BizException(
                f"这条{_HALL_NAMES.get(int(draft.post_type), '挂牌')}信息已经发布过了"
                f"（编号 {existing.post_no}），可以直接去「我发布的」里查看或修改"
            )

        result = EcoPublishService._run_precheck(draft, precheck, now)
        if result.blocked:
            raise BizException(result.block_message or "内容需要调整后才能发布")

        post = await EcoPublishService._insert_post(
            platform_db,
            draft=draft,
            publisher=publisher,
            precheck=result,
            now=now,
        )
        await EcoPublishService._insert_children(
            platform_db, post=post, draft=draft, publisher=publisher, now=now
        )

        ref_synced = await EcoPublishService._sync_ref(
            tenant_db, post=post, draft=draft
        )

        auto_listed = post.status == PostStatus.LISTED
        return PublishResult(
            post_id=int(post.id),
            post_no=post.post_no,
            status=post.status,
            audit_status=post.audit_status,
            auto_listed=auto_listed,
            suspicious_flags=list(result.suspicious_flags),
            hit_words=list(result.hit_words),
            ref_synced=ref_synced,
            message=EcoPublishService._success_message(draft, auto_listed),
        )

    # ------------------------------------------------------------------
    # 前置校验
    # ------------------------------------------------------------------

    @staticmethod
    def _assert_hall_enabled(publisher: PublisherContext) -> None:
        if publisher.hall_enabled:
            return
        reason = (publisher.disabled_reason or "").strip()
        tail = f"：{reason}" if reason else "，如有疑问请联系平台客服"
        raise BizException(f"贵公司的大厅发布功能已被暂时关闭{tail}")

    @staticmethod
    def _assert_draft_complete(draft: PostDraft) -> None:
        """落库前的完整性兜底

        这些字段在库里是非空约束，缺了会在最后一步抛数据库错误——那时用户已经
        填完整个表单，只能看到一句看不懂的报错。所以在这里拦住并说清缺什么。
        """
        if not draft.from_province:
            raise BizException("发货地址不完整，请补全省市信息后再发布")
        if not draft.window_start:
            raise BizException("请填写期望装车时间")
        if not (draft.title or "").strip():
            raise BizException("标题不能为空")
        if not (draft.contact_name or "").strip():
            raise BizException("请填写联系人姓名")
        if not (draft.contact_phone or "").strip():
            raise BizException("请填写联系电话")
        if int(draft.post_type) not in _EXT_MODELS:
            raise BizException("暂不支持这类信息的发布")
        if draft.valid_days <= 0:
            raise BizException("请选择展示天数")
        if draft.window_end and draft.window_start > draft.window_end:
            raise BizException("装车时间的开始时间不能晚于结束时间")

    @staticmethod
    async def _find_active_post(
        db: AsyncSession, tenant_code: str, draft: PostDraft
    ) -> Optional[SysEcoPost]:
        """同一源单是否已有非终态挂牌

        查平台库而不是租户库的 ref：ref 有可能因为双写窗口而缺失，
        用它查重会漏掉真实存在的挂牌，导致同一张任务单被挂两次。
        手工发布没有源单，天然无法查重，由前端防重复提交兜住。
        """
        if draft.source_id is None or int(draft.source_type) == SourceType.MANUAL:
            return None
        return (
            await db.execute(
                select(SysEcoPost)
                .where(
                    SysEcoPost.owner_tenant_code == tenant_code,
                    SysEcoPost.source_type == draft.source_type,
                    SysEcoPost.source_id == draft.source_id,
                    SysEcoPost.status.in_(PostStatus.OCCUPYING),
                    SysEcoPost.is_deleted == 0,
                )
                .limit(1)
            )
        ).scalars().first()

    @staticmethod
    def _run_precheck(
        draft: PostDraft, precheck: Optional[PrecheckInput], now: datetime
    ) -> PrecheckResult:
        return run_draft_precheck(draft, precheck, now)

    # ------------------------------------------------------------------
    # 平台库写入
    # ------------------------------------------------------------------

    @staticmethod
    async def _insert_post(
        db: AsyncSession,
        *,
        draft: PostDraft,
        publisher: PublisherContext,
        precheck: PrecheckResult,
        now: datetime,
    ) -> SysEcoPost:
        """写主表，编号冲突时重试

        用 SAVEPOINT 包住每次 flush：唯一索引冲突后只回滚这一次插入，
        不会把整个请求里其他已经准备好的写入一起废掉。
        """
        status, audit_status = EcoPublishService._initial_status(publisher, precheck)
        last_error: Optional[IntegrityError] = None

        for attempt in range(MAX_POST_NO_RETRY):
            post_no = await EcoNumberService.next_post_no(
                db, draft.post_type, prefer_db=attempt > 0
            )
            post = EcoPublishService._build_post(
                draft=draft,
                publisher=publisher,
                precheck=precheck,
                post_no=post_no,
                status=status,
                audit_status=audit_status,
                now=now,
            )
            try:
                async with db.begin_nested():
                    db.add(post)
                    await db.flush()
                return post
            except IntegrityError as e:
                last_error = e
                message = str(getattr(e, "orig", e)).lower()
                if "post_no" not in message and "duplicate entry" not in message:
                    raise
                logger.warning(
                    f"[Eco] 挂牌编号 {post_no} 冲突，改用库内水位重取（第 {attempt + 1} 次）"
                )

        raise BizException("发布失败，请稍后重试；若持续出现请联系管理员") from last_error

    @staticmethod
    def _initial_status(
        publisher: PublisherContext, precheck: PrecheckResult
    ) -> tuple:
        """决定初始状态

        免审白名单直通上架，但**命中可疑标记时收回直通资格**：白名单是对历史
        表现的信任，不是对单条内容的豁免。否则一旦白名单租户账号被盗用，
        违规内容会绕过全部人工环节直接进大厅。
        """
        if publisher.audit_whitelist and not precheck.suspicious_flags:
            return PostStatus.LISTED, AuditStatus.WHITELIST_PASS
        return PostStatus.AUDITING, AuditStatus.PENDING

    @staticmethod
    def _build_post(
        *,
        draft: PostDraft,
        publisher: PublisherContext,
        precheck: PrecheckResult,
        post_no: str,
        status: int,
        audit_status: int,
        now: datetime,
    ) -> SysEcoPost:
        masked = publisher.masked_name or mask_company_name(publisher.tenant_name)
        return SysEcoPost(
            post_no=post_no,
            post_type=int(draft.post_type),
            owner_tenant_code=publisher.tenant_code,
            owner_tenant_name=publisher.tenant_name,
            owner_masked_name=masked,
            publisher_user_id=publisher.user_id,
            publisher_name=publisher.user_name,
            title=draft.title.strip(),
            status=status,
            source_type=int(draft.source_type),
            source_id=draft.source_id,
            source_snapshot_at=draft.source_snapshot_at or now,
            valid_from=now,
            valid_until=now + timedelta(days=int(draft.valid_days)),
            from_province=draft.from_province,
            from_city=draft.from_city,
            from_district=draft.from_district,
            from_region_code=draft.from_region_code,
            from_name=draft.from_name,
            to_province=draft.to_province,
            to_city=draft.to_city,
            to_district=draft.to_district,
            to_region_code=draft.to_region_code,
            to_name=draft.to_name,
            any_direction=int(draft.any_direction),
            window_start=draft.window_start,
            window_end=draft.window_end,
            total_quantity=draft.total_quantity,
            quantity_unit=draft.quantity_unit or "台",
            remaining_quantity=draft.remaining_quantity,
            price_type=int(draft.price_type),
            price_amount=draft.price_amount,
            price_include_tax=int(draft.price_include_tax),
            price_negotiable=int(draft.price_negotiable),
            cooperation_type=int(draft.cooperation_type),
            keep_listed_after_deal=int(draft.keep_listed_after_deal),
            contact_name=draft.contact_name,
            contact_phone=draft.contact_phone,
            contact_backup=draft.contact_backup,
            visibility_level=int(draft.visibility_level),
            contact_visibility=int(draft.contact_visibility),
            apply_block_rule=int(draft.apply_block_rule),
            extra_block_tenants=draft.extra_block_tenants or None,
            audit_status=audit_status,
            # 免审直通也记进队时间：它进的是抽检队列，同样要算「等了多久」
            submitted_at=now,
            precheck_flags=list(precheck.suspicious_flags) or None,
            listed_at=now if status == PostStatus.LISTED else None,
            last_active_at=now,
        )

    @staticmethod
    async def _insert_children(
        db: AsyncSession,
        *,
        post: SysEcoPost,
        draft: PostDraft,
        publisher: PublisherContext,
        now: datetime,
    ) -> None:
        """写扩展表、目的地、流转审计"""
        ext_model = _EXT_MODELS[int(draft.post_type)]
        db.add(ext_model(post_id=post.id, **(draft.ext or {})))

        for dest in draft.destinations:
            if not dest.province:
                continue
            db.add(
                SysEcoPostDest(
                    post_id=post.id,
                    post_type=int(draft.post_type),
                    province=dest.province,
                    city=dest.city,
                    region_code=dest.region_code,
                    sort_order=dest.sort_order,
                )
            )

        auto_listed = post.status == PostStatus.LISTED
        db.add(
            SysEcoPostAudit(
                post_id=post.id,
                action=(
                    PostAuditAction.WHITELIST_PASS
                    if auto_listed
                    else PostAuditAction.SUBMIT
                ),
                from_status=PostStatus.DRAFT,
                to_status=post.status,
                operator_type=OperatorType.TENANT_USER,
                operator_id=publisher.user_id,
                operator_name=publisher.user_name,
                operator_tenant_code=publisher.tenant_code,
                reason="免审白名单直通上架" if auto_listed else "提交审核",
            )
        )
        await db.flush()

    # ------------------------------------------------------------------
    # 租户库镜像
    # ------------------------------------------------------------------

    @staticmethod
    async def _sync_ref(
        tenant_db: AsyncSession, *, post: SysEcoPost, draft: PostDraft
    ) -> bool:
        """写租户侧镜像

        **失败不阻断发布**：挂牌已经在平台库建好了，为了一个展示用的角标把整个
        发布回滚掉，对用户是更差的结果。这里吞掉异常并标记 ``sync_pending``，
        由巡检 Worker 补偿。查重不依赖本表，所以缺失是安全的（见模块注释）。
        """
        ref = BizEcoPostRef(
            source_type=int(draft.source_type),
            source_id=draft.source_id,
            post_id=int(post.id),
            post_no=post.post_no,
            post_type=int(draft.post_type),
            post_status=int(post.status),
            sync_pending=0,
            last_sync_at=datetime.now(),
        )
        try:
            async with tenant_db.begin_nested():
                tenant_db.add(ref)
                await tenant_db.flush()
            return True
        except Exception as e:
            logger.error(
                f"[Eco] 挂牌 {post.post_no} 的租户侧镜像写入失败，待巡检补偿：{e}"
            )
            return False

    # ------------------------------------------------------------------

    @staticmethod
    def _success_message(draft: PostDraft, auto_listed: bool) -> str:
        hall = _HALL_NAMES.get(int(draft.post_type), "大厅")
        if auto_listed:
            return f"已发布到{hall}，现在同行就能看到了"
        return f"已提交发布，平台审核通过后会出现在{hall}，通常 2 小时内完成"
