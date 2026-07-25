"""挂牌管理：编辑 / 提交 / 停止展示 / 重新上架 / 延长展示

对应 08.接口契约.md §3.6。发布之后的全生命周期动作都收在这里，
状态流转的合法性交给 ``post_state_machine``，编辑分档交给 ``post_edit_policy``。

## 越权防线

所有入口只有一个取数函数 ``_load_own_post``，条件里恒带
``owner_tenant_code = 当前租户``，并且**「不存在」与「不属于你」返回同一句话**。
两者文案分开等于给外部提供了一个跨租户的存在性探测器：拿 ID 遍历一遍，
就能数出别家有多少条挂牌。

## 编辑与进行中洽谈的关系

改核心信息会让挂牌回到待审核、从大厅移出，但**已有的意向一律不动**。
洽谈是双方已经建立起来的关系，不能因为发布方把装车时间往后挪了一天，
系统就单方面把三家正在谈的同行踢掉。改了哪些项记在流转流水里，
后续给洽谈方推「对方更新了信息」用的就是这份数据。

停止展示则相反：挂牌不在了，还挂着「待响应」的意向就是让人白等，
所以待响应与洽谈中的意向一并失效。**已选定的意向不动**——它背后有成交单
在跑，把意向作废会让成交单失去来源。

## 有效期只有一条修改路径

编辑不碰 ``valid_from`` / ``valid_until``，只有「延长展示」能改。
否则反复保存就能无限续命，把展示天数上限绕空。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.services.ecosystem.content_guard import (
    PrecheckInput,
    PrecheckResult,
    SuspiciousFlag,
    run_precheck,
)
from app.modules.client.services.ecosystem.post_draft import (
    PostDraft,
    run_draft_precheck,
)
from app.modules.client.services.ecosystem.post_edit_policy import (
    MAIN_FIELDS,
    EditDiff,
    build_diff,
)
from app.modules.client.services.ecosystem.post_ref_sync import mirror_post_status
from app.modules.client.services.ecosystem.post_state_machine import (
    assert_transit,
    describe,
    is_editable,
)
from app.modules.console.models.ecosystem.capacity_post import SysEcoCapacityPost
from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost
from app.modules.console.models.ecosystem.constants import (
    DEFAULT_VALID_DAYS,
    MAX_VALID_DAYS,
    MAX_VALID_DAYS_LONG_TERM,
    VALID_DAYS_OPTIONS,
    AuditStatus,
    CooperationType,
    DelistReason,
    IntentInvalidReason,
    OperatorType,
    PostAuditAction,
    PostStatus,
    PostType,
)
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest
from app.modules.console.services.ecosystem.intent_lifecycle import (
    InvalidatedIntent,
    invalidate_active_intents,
)

_EXT_MODELS = {
    PostType.CARGO: SysEcoCargoPost,
    PostType.CAPACITY: SysEcoCapacityPost,
}

_HALL_NAMES = {PostType.CARGO: "货源大厅", PostType.CAPACITY: "运力大厅"}

# 各状态下不能继续操作时给用户的下一步建议。缺了这些，用户只会看到
# 「不能停止展示」而不知道该去哪儿处理
_ADVICE_BY_STATUS: Dict[int, str] = {
    PostStatus.AUDITING: "审核结果出来后就可以操作了，通常 2 小时内完成",
    PostStatus.LOCKED: "已经选定了合作方，请先在「我的合作」里处理这次合作",
    PostStatus.FULFILLING: "合作正在履约中，需要终止请在「我的合作」里处理",
    PostStatus.FINISHED: "这次合作已经完成，可以重新发布一条新的",
    PostStatus.CANCELLED: "这条已经取消了，可以重新发布一条新的",
}


@dataclass
class OwnerContext:
    """操作人身份

    ``audit_whitelist`` 来自 ``sys_eco_tenant_credit.audit_whitelist``，
    由调用方查库带入，语义与发布链路完全一致。
    """

    tenant_code: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    audit_whitelist: bool = False


@dataclass
class ManageResult:
    """挂牌管理动作的统一结果

    五个动作共用一个结果类型，是为了让 API 层不必为每个动作各写一套出参——
    它们要回给前端的东西高度重合（新状态 + 一句话 + 是否需要重审）。
    """

    post_id: int
    post_no: str
    status: int
    audit_status: int
    message: str
    # 对应 08 §3.6 的 requireReaudit：这次操作是否把挂牌从大厅移出去重审了
    require_reaudit: bool = False
    changed_labels: List[str] = field(default_factory=list)
    suspicious_flags: List[str] = field(default_factory=list)
    hit_words: List[str] = field(default_factory=list)
    invalidated_intents: List[InvalidatedIntent] = field(default_factory=list)
    valid_until: Optional[datetime] = None
    # 租户侧角标是否已同步。False 表示角标暂时不准，待巡检修正，不是失败
    ref_synced: bool = True


class EcoPostManageService:
    """挂牌管理"""

    # ==================================================================
    # 编辑
    # ==================================================================

    @staticmethod
    async def edit(
        *,
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        post_id: int,
        owner: OwnerContext,
        draft: PostDraft,
        precheck: Optional[PrecheckInput] = None,
        now: Optional[datetime] = None,
    ) -> ManageResult:
        """编辑挂牌

        Args:
            draft: 由 Builder 用新表单重新构建的完整草稿。走 Builder 而不是
                接一个「改动字段字典」，是为了让编辑复用发布的全部校验
                （证照有效期、地区解析、标题生成），否则这些规则会在编辑
                路径上集体失效。
        """
        now = now or datetime.now()
        post = await EcoPostManageService._load_own_post(
            platform_db, post_id, owner.tenant_code
        )

        if not is_editable(post.status):
            raise BizException(
                f"这条挂牌现在是「{describe(post.status)}」，不能修改"
                f"{_advice_tail(post.status)}"
            )
        if int(post.post_type) != int(draft.post_type):
            raise BizException("挂牌类型不能修改，如需换类型请重新发布一条")

        ext = await EcoPostManageService._load_ext(platform_db, post)
        dests = await EcoPostManageService._load_dests(platform_db, post)
        diff = build_diff(post=post, ext=ext, dests=dests, draft=draft)
        if not diff.has_changes:
            return EcoPostManageService._result(
                post, message="内容没有变化，不用重复保存"
            )

        EcoPostManageService._assert_quantity_covers_dealt(post, draft)

        result = run_draft_precheck(draft, precheck, now)
        if result.blocked:
            raise BizException(result.block_message or "内容需要调整后才能发布")

        from_status = int(post.status)
        from_audit_status = int(post.audit_status)
        EcoPostManageService._apply_draft(post, draft, now)
        EcoPostManageService._apply_ext(platform_db, post, ext, draft)
        EcoPostManageService._rewrite_dests(platform_db, post, dests, draft, diff)

        to_status, audit_status = EcoPostManageService._status_after_edit(
            from_status=from_status,
            from_audit_status=from_audit_status,
            diff=diff,
            precheck=result,
            owner=owner,
        )
        assert_transit(from_status, to_status, action="修改")
        post.status = to_status
        post.audit_status = audit_status
        post.precheck_flags = list(result.suspicious_flags) or None

        require_reaudit = to_status != from_status
        if require_reaudit:
            # 重新排队了，上一轮的驳回理由与审核人必须清掉，否则「我发布的」
            # 会一直挂着一条已经改过的驳回原因，用户以为又被驳了
            post.audit_reason = None
            post.audit_at = None
            post.audit_by = None
            # 重新进队就重新开始计时，否则这条挂牌在运营队列里看起来
            # 从第一次提交时就在等，一进队就是超时状态
            post.submitted_at = now
        ref_synced = True
        if require_reaudit:
            ref_synced = await mirror_post_status(
                tenant_db,
                post_id=int(post.id),
                post_no=post.post_no,
                status=to_status,
                now=now,
            )

        EcoPostManageService._write_audit(
            platform_db,
            post=post,
            action=PostAuditAction.EDIT,
            from_status=from_status,
            to_status=to_status,
            owner=owner,
            reason="修改了" + "、".join(diff.labels),
            changed_fields=diff.to_audit_payload(),
        )
        await platform_db.flush()

        return EcoPostManageService._result(
            post,
            message=EcoPostManageService._edit_message(post, diff, require_reaudit),
            require_reaudit=require_reaudit,
            changed_labels=diff.labels,
            precheck=result,
            ref_synced=ref_synced,
        )

    @staticmethod
    def _status_after_edit(
        *,
        from_status: int,
        from_audit_status: int,
        diff: EditDiff,
        precheck: PrecheckResult,
        owner: OwnerContext,
    ) -> tuple:
        """编辑后的状态与审核状态

        只有「展示中」的挂牌会因为编辑而改变状态。草稿、驳回态、已下架的挂牌
        编辑后留在原状态、审核状态也不动：让它们自动进审核队列，用户就失去了
        「先存着，改好了再提交」的空间；驳回理由留着也正好提醒还有什么没改。

        快速复审保持原审核状态，不改写成「通过」：原本是免审直通待抽检的挂牌，
        被一次改联系人就洗成正式通过，抽检队列里就再也找不到它了。

        命中可疑标记时，快速复审升级为完整重审——预检放过但需要人看一眼的
        内容，不能继续留在大厅里。免审白名单同理被收回，与发布链路一致。
        """
        if from_status != PostStatus.LISTED:
            return from_status, from_audit_status

        needs_review = diff.requires_full_reaudit or bool(precheck.suspicious_flags)
        if not needs_review:
            return PostStatus.LISTED, from_audit_status
        if owner.audit_whitelist and not precheck.suspicious_flags:
            return PostStatus.LISTED, AuditStatus.WHITELIST_PASS
        return PostStatus.AUDITING, AuditStatus.PENDING

    @staticmethod
    def _edit_message(
        post: SysEcoPost, diff: EditDiff, require_reaudit: bool
    ) -> str:
        items = "、".join(diff.labels)
        if require_reaudit:
            hall = _HALL_NAMES.get(int(post.post_type), "大厅")
            return (
                f"已保存对{items}的修改。因为改动了关键信息，这条挂牌需要重新审核，"
                f"审核通过后会回到{hall}；正在洽谈的同行不受影响"
            )
        return f"已保存对{items}的修改，同行看到的就是最新信息了"

    # ==================================================================
    # 提交审核
    # ==================================================================

    @staticmethod
    async def submit(
        *,
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        post_id: int,
        owner: OwnerContext,
        precheck: Optional[PrecheckInput] = None,
        valid_days: Optional[int] = None,
        now: Optional[datetime] = None,
    ) -> ManageResult:
        """把草稿或被驳回的挂牌提交审核"""
        now = now or datetime.now()
        post = await EcoPostManageService._load_own_post(
            platform_db, post_id, owner.tenant_code
        )

        if int(post.status) == PostStatus.AUDITING:
            return EcoPostManageService._result(
                post, message="这条挂牌已经在审核中了，通常 2 小时内会有结果"
            )
        if int(post.status) == PostStatus.LISTED:
            # 「展示中 → 待审核」在状态机里是合法的（编辑核心信息要重审），
            # 但提交审核不该走这条路：好好挂着的信息会被白白撤出大厅
            raise BizException("这条挂牌正在展示中，不用再提交审核")
        if int(post.status) == PostStatus.DELISTED:
            raise BizException("这条挂牌已经停止展示了，想重新挂出去请用「重新上架」")
        assert_transit(
            post.status,
            PostStatus.AUDITING,
            action="提交审核",
            advice=_advice(post.status),
        )

        was_rejected = int(post.status) == PostStatus.REJECTED
        result = await EcoPostManageService._run_stored_precheck(
            platform_db, post, precheck, now
        )
        if result.blocked:
            raise BizException(result.block_message or "内容需要调整后才能提交")

        from_status = int(post.status)
        # 被人工驳回过的挂牌不给免审直通：驳回是人看过之后的判断，
        # 改完再直通上架等于让用户自己决定驳回意见有没有落实
        auto_pass = (
            owner.audit_whitelist and not was_rejected and not result.suspicious_flags
        )
        post.status = PostStatus.LISTED if auto_pass else PostStatus.AUDITING
        post.audit_status = (
            AuditStatus.WHITELIST_PASS if auto_pass else AuditStatus.PENDING
        )
        post.audit_reason = None
        post.audit_at = None
        post.audit_by = None
        post.precheck_flags = list(result.suspicious_flags) or None
        post.submitted_at = now
        # 草稿可能躺了很多天，原有效期早过了，直接上架会「上架即过期」
        EcoPostManageService._reset_validity(post, valid_days, now)
        if auto_pass and post.listed_at is None:
            post.listed_at = now
        post.last_active_at = now

        ref_synced = await mirror_post_status(
            tenant_db,
            post_id=int(post.id),
            post_no=post.post_no,
            status=int(post.status),
            now=now,
        )
        EcoPostManageService._write_audit(
            platform_db,
            post=post,
            action=(
                PostAuditAction.WHITELIST_PASS
                if auto_pass
                else (
                    PostAuditAction.RESUBMIT if was_rejected else PostAuditAction.SUBMIT
                )
            ),
            from_status=from_status,
            to_status=int(post.status),
            owner=owner,
            reason="修改后重新提交" if was_rejected else "提交审核",
        )
        await platform_db.flush()

        hall = _HALL_NAMES.get(int(post.post_type), "大厅")
        return EcoPostManageService._result(
            post,
            message=(
                f"已发布到{hall}，现在同行就能看到了"
                if auto_pass
                else f"已提交，平台审核通过后会出现在{hall}，通常 2 小时内完成"
            ),
            precheck=result,
            ref_synced=ref_synced,
        )

    # ==================================================================
    # 停止展示
    # ==================================================================

    @staticmethod
    async def delist(
        *,
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        post_id: int,
        owner: OwnerContext,
        remark: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> ManageResult:
        """发布方主动停止展示"""
        now = now or datetime.now()
        post = await EcoPostManageService._load_own_post(
            platform_db, post_id, owner.tenant_code
        )

        if int(post.status) == PostStatus.DELISTED:
            return EcoPostManageService._result(
                post, message="这条挂牌已经停止展示了"
            )
        assert_transit(
            post.status,
            PostStatus.DELISTED,
            action="停止展示",
            advice=_advice(post.status),
        )

        from_status = int(post.status)
        post.status = PostStatus.DELISTED
        post.delist_reason = DelistReason.BY_OWNER
        post.delist_remark = (remark or "").strip() or None
        post.last_active_at = now

        invalidated = await EcoPostManageService._invalidate_intents(
            platform_db, post, now
        )
        ref_synced = await mirror_post_status(
            tenant_db,
            post_id=int(post.id),
            post_no=post.post_no,
            status=PostStatus.DELISTED,
            now=now,
        )
        EcoPostManageService._write_audit(
            platform_db,
            post=post,
            action=PostAuditAction.DELIST_BY_OWNER,
            from_status=from_status,
            to_status=PostStatus.DELISTED,
            owner=owner,
            reason=post.delist_remark or "发布方主动停止展示",
        )
        await platform_db.flush()

        if invalidated:
            message = (
                f"已停止展示。有 {len(invalidated)} 家同行正在洽谈，"
                f"他们会收到这条信息已撤下的通知"
            )
        else:
            message = "已停止展示，同行不会再看到这条信息"
        return EcoPostManageService._result(
            post,
            message=message,
            invalidated_intents=invalidated,
            ref_synced=ref_synced,
        )

    # ==================================================================
    # 重新上架
    # ==================================================================

    @staticmethod
    async def relist(
        *,
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        post_id: int,
        owner: OwnerContext,
        valid_days: Optional[int] = None,
        precheck: Optional[PrecheckInput] = None,
        now: Optional[datetime] = None,
    ) -> ManageResult:
        """重新上架

        一律回待审核，**不给免审直通**。白名单是对租户历史表现的信任，
        而被下架过的恰恰是这条内容本身，正是需要重新看一眼的对象
        （`01` §4.2：不能让用户下架再上架来绕过处置）。
        """
        now = now or datetime.now()
        post = await EcoPostManageService._load_own_post(
            platform_db, post_id, owner.tenant_code
        )

        if int(post.status) == PostStatus.AUDITING:
            return EcoPostManageService._result(
                post, message="这条挂牌已经在审核中了，通常 2 小时内会有结果"
            )
        if int(post.status) == PostStatus.LISTED:
            return EcoPostManageService._result(
                post, message="这条挂牌正在展示中，不用重新上架"
            )
        assert_transit(
            post.status,
            PostStatus.AUDITING,
            action="重新上架",
            advice=_advice(post.status),
        )
        EcoPostManageService._assert_window_not_passed(post, now)

        was_forced = int(post.delist_reason or 0) == DelistReason.FORCED
        result = await EcoPostManageService._run_stored_precheck(
            platform_db, post, precheck, now
        )
        if result.blocked:
            raise BizException(result.block_message or "内容需要调整后才能重新上架")
        if was_forced:
            # 处置历史必须跟着这条挂牌走到审核台前，否则运营会把同一条违规内容
            # 当成新挂牌重新放行
            result.suspicious_flags.append(SuspiciousFlag.WAS_FORCE_DELISTED)
            result.suspicious_notes.append(
                f"这条挂牌曾被平台强制下架：{post.delist_remark or '未填说明'}"
            )

        from_status = int(post.status)
        post.status = PostStatus.AUDITING
        post.audit_status = AuditStatus.PENDING
        post.delist_reason = None
        post.delist_remark = None
        post.audit_reason = None
        post.audit_at = None
        post.audit_by = None
        post.precheck_flags = list(result.suspicious_flags) or None
        post.submitted_at = now
        # 有效期必须重算：绝大多数下架就是因为到期，沿用旧的等于上架即过期
        EcoPostManageService._reset_validity(post, valid_days, now)
        post.last_active_at = now

        ref_synced = await mirror_post_status(
            tenant_db,
            post_id=int(post.id),
            post_no=post.post_no,
            status=PostStatus.AUDITING,
            now=now,
        )
        EcoPostManageService._write_audit(
            platform_db,
            post=post,
            action=PostAuditAction.RELIST,
            from_status=from_status,
            to_status=PostStatus.AUDITING,
            owner=owner,
            reason="重新上架，重新提交审核",
        )
        await platform_db.flush()

        hall = _HALL_NAMES.get(int(post.post_type), "大厅")
        return EcoPostManageService._result(
            post,
            message=(
                f"已提交重新上架，平台审核通过后会回到{hall}，通常 2 小时内完成"
            ),
            require_reaudit=True,
            precheck=result,
            ref_synced=ref_synced,
        )

    # ==================================================================
    # 延长展示
    # ==================================================================

    @staticmethod
    async def extend(
        *,
        platform_db: AsyncSession,
        post_id: int,
        owner: OwnerContext,
        days: int,
        now: Optional[datetime] = None,
    ) -> ManageResult:
        """延长展示天数

        不改状态，所以不需要回写租户库镜像。已下架的走「重新上架」而不是这里：
        重新上架要重审，延长展示不需要，两者混在一起就等于给了一条
        「过期后延一天即可继续展示、永不复审」的路。
        """
        now = now or datetime.now()
        if int(days) not in VALID_DAYS_OPTIONS:
            options = "、".join(str(d) for d in VALID_DAYS_OPTIONS)
            raise BizException(f"展示天数请选择 {options} 天")

        post = await EcoPostManageService._load_own_post(
            platform_db, post_id, owner.tenant_code
        )
        if int(post.status) != PostStatus.LISTED:
            advice = (
                "想重新挂出去请用「重新上架」"
                if int(post.status) == PostStatus.DELISTED
                else _advice(post.status)
            )
            raise BizException(
                f"这条挂牌现在是「{describe(post.status)}」，不能延长展示"
                + (f"，{advice}" if advice else "")
            )

        # 从「较晚的那个时间」起算：对刚过期还没被巡检扫到的挂牌，
        # 从旧的 valid_until 起算会延完还是过期状态
        base = max(now, post.valid_until)
        limit_days = (
            MAX_VALID_DAYS_LONG_TERM
            if int(post.cooperation_type) == CooperationType.LONG_TERM
            else MAX_VALID_DAYS
        )
        cap = post.valid_from + timedelta(days=limit_days)
        new_until = base + timedelta(days=int(days))
        if new_until > cap:
            raise BizException(
                f"一条挂牌最多展示 {limit_days} 天，这条已经排到 "
                f"{post.valid_until:%Y-%m-%d}，不能再延了；"
                f"还想继续找同行，可以停止展示后重新发布一条"
            )

        post.valid_until = new_until
        post.last_active_at = now
        EcoPostManageService._write_audit(
            platform_db,
            post=post,
            action=PostAuditAction.EXTEND,
            from_status=PostStatus.LISTED,
            to_status=PostStatus.LISTED,
            owner=owner,
            reason=f"延长展示 {int(days)} 天",
        )
        await platform_db.flush()

        return EcoPostManageService._result(
            post,
            message=f"已延长展示到 {new_until:%Y-%m-%d}，同行还能继续看到这条信息",
        )

    # ==================================================================
    # 取数
    # ==================================================================

    @staticmethod
    async def _load_own_post(
        db: AsyncSession, post_id: int, tenant_code: str, *, lock: bool = True
    ) -> SysEcoPost:
        """按归属取挂牌

        ``owner_tenant_code`` 写在 WHERE 里而不是取出来再断言：写在 WHERE 里
        漏不掉，取出来再判会在某次重构中被顺手删掉。找不到与不属于你返回
        同一句话，不给外部留跨租户的存在性探测口子。
        """
        if not tenant_code:
            raise ValueError("tenant_code 不能为空：挂牌管理必须带归属租户身份")
        stmt = select(SysEcoPost).where(
            SysEcoPost.id == int(post_id),
            SysEcoPost.owner_tenant_code == tenant_code,
            SysEcoPost.is_deleted == 0,
        )
        if lock:
            # 编辑与下架都是读-改-写，两个标签页同时点会互相覆盖状态
            stmt = stmt.with_for_update()
        post = (await db.execute(stmt)).scalars().first()
        if post is None:
            raise BizException("没找到这条挂牌，它可能已经被删除了")
        return post

    @staticmethod
    async def _load_ext(db: AsyncSession, post: SysEcoPost) -> Any:
        model = _EXT_MODELS.get(int(post.post_type))
        if model is None:
            return None
        return (
            await db.execute(
                select(model).where(
                    model.post_id == int(post.id), model.is_deleted == 0
                )
            )
        ).scalars().first()

    @staticmethod
    async def _load_dests(
        db: AsyncSession, post: SysEcoPost
    ) -> Sequence[SysEcoPostDest]:
        return (
            await db.execute(
                select(SysEcoPostDest)
                .where(
                    SysEcoPostDest.post_id == int(post.id),
                    SysEcoPostDest.is_deleted == 0,
                )
                .order_by(SysEcoPostDest.sort_order.asc())
            )
        ).scalars().all()

    # ==================================================================
    # 写入
    # ==================================================================

    @staticmethod
    def _apply_draft(post: SysEcoPost, draft: PostDraft, now: datetime) -> None:
        """把草稿写回主表

        字段清单直接取自 ``MAIN_FIELDS``：分级表与实际写入的字段必须是同一份，
        否则会出现「表里没登记所以不判重审、但值确实被改掉了」的静默漏洞。
        有效期不在表里，也就不会被这里碰到。
        """
        dealt = _dealt_quantity(post)
        for name in MAIN_FIELDS:
            setattr(post, name, getattr(draft, name, None))

        if draft.total_quantity is None or draft.remaining_quantity is None:
            post.remaining_quantity = draft.remaining_quantity
        else:
            # 已被同行接走的量不能因为改台数而复活
            post.remaining_quantity = max(0, int(draft.total_quantity) - dealt)

        post.source_snapshot_at = draft.source_snapshot_at or now
        # 用户已经按最新情况改过一遍了，「信息已变更」的催更标记该清掉，
        # 否则 48 小时后会被巡检当成没更新而自动下架
        post.source_changed = 0
        post.source_changed_at = None
        post.last_active_at = now

    @staticmethod
    def _apply_ext(
        db: AsyncSession, post: SysEcoPost, ext: Any, draft: PostDraft
    ) -> None:
        """写扩展表，只覆盖草稿里出现的键（与 ``diff_ext`` 的口径一致）"""
        if not draft.ext:
            return
        if ext is None:
            model = _EXT_MODELS[int(post.post_type)]
            db.add(model(post_id=int(post.id), **draft.ext))
            return
        for name, value in draft.ext.items():
            setattr(ext, name, value)

    @staticmethod
    def _rewrite_dests(
        db: AsyncSession,
        post: SysEcoPost,
        dests: Sequence[SysEcoPostDest],
        draft: PostDraft,
        diff: EditDiff,
    ) -> None:
        """目的地有变化时整体重写

        逐行比对更新省不下什么（一条挂牌通常 1~3 个目的地），却要处理新增、
        删除、换序三种情况。整体重写只有一种情况要处理。
        """
        if "destinations" not in diff.field_names:
            return
        for row in dests:
            row.is_deleted = 1
        for dest in draft.destinations:
            if not dest.province:
                continue
            db.add(
                SysEcoPostDest(
                    post_id=int(post.id),
                    post_type=int(post.post_type),
                    province=dest.province,
                    city=dest.city,
                    region_code=dest.region_code,
                    sort_order=dest.sort_order,
                )
            )

    @staticmethod
    async def _invalidate_intents(
        db: AsyncSession, post: SysEcoPost, now: datetime
    ) -> List[InvalidatedIntent]:
        """下架时让待响应与洽谈中的意向失效

        实现在 ``intent_lifecycle`` 里与运营强制下架共用一份：挂牌不在了要收口
        意向，这件事和「是谁把它下架的」无关。
        """
        return await invalidate_active_intents(
            db, post=post, reason=IntentInvalidReason.POST_DELISTED, now=now
        )

    @staticmethod
    def _write_audit(
        db: AsyncSession,
        *,
        post: SysEcoPost,
        action: int,
        from_status: int,
        to_status: int,
        owner: OwnerContext,
        reason: Optional[str] = None,
        changed_fields: Optional[dict] = None,
    ) -> None:
        db.add(
            SysEcoPostAudit(
                post_id=int(post.id),
                action=int(action),
                from_status=int(from_status),
                to_status=int(to_status),
                operator_type=OperatorType.TENANT_USER,
                operator_id=owner.user_id,
                operator_name=owner.user_name,
                operator_tenant_code=owner.tenant_code,
                reason=(reason or "")[:255] or None,
                changed_fields=changed_fields,
            )
        )

    # ==================================================================
    # 校验与工具
    # ==================================================================

    @staticmethod
    def _assert_quantity_covers_dealt(post: SysEcoPost, draft: PostDraft) -> None:
        """改台数不能改到比已成交的还少"""
        dealt = _dealt_quantity(post)
        if not dealt or draft.total_quantity is None:
            return
        if int(draft.total_quantity) < dealt:
            unit = post.quantity_unit or "台"
            raise BizException(
                f"已经有 {dealt}{unit} 被同行接走了，总量不能改到比这个还少"
            )

    @staticmethod
    def _assert_window_not_passed(post: SysEcoPost, now: datetime) -> None:
        if post.window_start and post.window_start < now:
            raise BizException(
                f"原来填的时间（{post.window_start:%m月%d日}）已经过了，"
                f"请先修改时间安排再重新上架"
            )

    @staticmethod
    def _reset_validity(
        post: SysEcoPost, valid_days: Optional[int], now: datetime
    ) -> None:
        """重置展示周期

        没指定天数时沿用这条挂牌原来的展示跨度，用户不用再选一次；
        原跨度算不出来（数据异常）时退回默认天数，而不是让它上架即过期。
        """
        days = EcoPostManageService._resolve_valid_days(post, valid_days)
        post.valid_from = now
        post.valid_until = now + timedelta(days=days)

    @staticmethod
    def _resolve_valid_days(post: SysEcoPost, valid_days: Optional[int]) -> int:
        if valid_days is not None:
            if int(valid_days) not in VALID_DAYS_OPTIONS:
                options = "、".join(str(d) for d in VALID_DAYS_OPTIONS)
                raise BizException(f"展示天数请选择 {options} 天")
            return int(valid_days)
        limit = (
            MAX_VALID_DAYS_LONG_TERM
            if int(post.cooperation_type) == CooperationType.LONG_TERM
            else MAX_VALID_DAYS
        )
        span = 0
        if post.valid_from and post.valid_until:
            span = (post.valid_until - post.valid_from).days
        if span <= 0:
            return DEFAULT_VALID_DAYS
        return min(span, limit)

    @staticmethod
    async def _run_stored_precheck(
        db: AsyncSession,
        post: SysEcoPost,
        precheck: Optional[PrecheckInput],
        now: datetime,
    ) -> PrecheckResult:
        """对库里已有的挂牌跑预检

        提交与重新上架都不改内容，重跑预检看起来多余，其实是必要的：
        敏感词库是运营在线维护的，上次发布时干净的文本，这次可能已经命中新词。

        自由文本由调用方装进 ``precheck.texts``（它才知道该按哪个大厅取扩展表
        字段）；线路与时间从库里的挂牌补齐，避免调用方漏传导致规则空转。
        """
        if precheck is None:
            return PrecheckResult()
        precheck.from_province = post.from_province
        precheck.from_city = post.from_city
        precheck.from_district = post.from_district
        precheck.to_province = post.to_province
        precheck.to_city = post.to_city
        precheck.to_district = post.to_district
        precheck.window_start = post.window_start
        precheck.now = precheck.now or now
        precheck.texts = {
            **({"标题": post.title} if post.title else {}),
            **(precheck.texts or {}),
        }
        return run_precheck(precheck)

    @staticmethod
    def _result(
        post: SysEcoPost,
        *,
        message: str,
        require_reaudit: bool = False,
        changed_labels: Optional[List[str]] = None,
        precheck: Optional[PrecheckResult] = None,
        invalidated_intents: Optional[List[InvalidatedIntent]] = None,
        ref_synced: bool = True,
    ) -> ManageResult:
        return ManageResult(
            post_id=int(post.id),
            post_no=post.post_no,
            status=int(post.status),
            audit_status=int(post.audit_status),
            message=message,
            require_reaudit=require_reaudit,
            changed_labels=list(changed_labels or []),
            suspicious_flags=list(precheck.suspicious_flags) if precheck else [],
            hit_words=list(precheck.hit_words) if precheck else [],
            invalidated_intents=list(invalidated_intents or []),
            valid_until=post.valid_until,
            ref_synced=ref_synced,
        )


# ---------------------------------------------------------------------------


def _dealt_quantity(post: SysEcoPost) -> int:
    """已被接走的量。不分批（``remaining_quantity`` 为空）时恒为 0"""
    if post.total_quantity is None or post.remaining_quantity is None:
        return 0
    return max(0, int(post.total_quantity) - int(post.remaining_quantity))


def _advice(status: Optional[int]) -> Optional[str]:
    if status is None:
        return None
    return _ADVICE_BY_STATUS.get(int(status))


def _advice_tail(status: Optional[int]) -> str:
    advice = _advice(status)
    return f"，{advice}" if advice else ""
