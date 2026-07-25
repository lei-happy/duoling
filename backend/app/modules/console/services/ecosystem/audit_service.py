"""运营审核动作：通过 / 驳回 / 批量通过 / 强制下架 / 抽检

对应 08.接口契约.md §4.1 与 04.运营审核与风控设计.md §2。

## 与租户端 post_manage_service 的分工

同一张挂牌，两侧都能改状态，但改的理由完全不同：租户改的是「我的信息」，
运营改的是「这条信息能不能对外」。合法流转由共用的 ``post_state_machine``
判定，谁有资格触发由各自 Service 判定——所以这里的取数函数**不带
``owner_tenant_code`` 条件**（运营本来就要跨租户操作），而租户端恒带。

## 为什么运营侧也要回写租户库

租户库的 ``biz_eco_post_ref.post_status`` 是任务单列表 / 运力列表上那个
「已发布到货源大厅」角标的数据源。运营通过审核后不回写，租户在自己的业务页面上
就还看到「审核中」，只有点进服务平台才能发现已经上架了。运营端没有租户库
Session，所以这里按 ``owner_tenant_code`` 临时开一个；写失败只记日志，
交巡检补偿——为一个角标回滚掉审核结论是不划算的。

## 批量通过的事务边界

逐条一个 SAVEPOINT（08 §5）。某一条因为状态已变而失败，只回滚它自己，
其余照常通过。不用一个大事务，是因为运营勾了 50 条点通过，
最不能接受的结果是「其中一条不行，50 条全没动，且不告诉你是哪条」。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.core.database import db_manager
from app.modules.client.services.ecosystem.post_ref_sync import mirror_post_status
from app.modules.client.services.ecosystem.post_state_machine import (
    can_transit,
    describe,
)
from app.modules.console.models.ecosystem.constants import (
    DEFAULT_VALID_DAYS,
    MAX_BATCH_APPROVE,
    MAX_VALID_DAYS,
    MAX_VALID_DAYS_LONG_TERM,
    REJECT_REASON_LABELS,
    AuditStatus,
    CooperationType,
    DelistReason,
    IntentInvalidReason,
    OperatorType,
    PostAuditAction,
    PostRejectReason,
    PostStatus,
    PostType,
)
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.services.ecosystem.audit_query_service import OpsContext
from app.modules.console.services.ecosystem.intent_lifecycle import (
    InvalidatedIntent,
    invalidate_active_intents,
)
from app.modules.console.services.ecosystem.whitelist_service import (
    EcoWhitelistService,
)

_HALL_NAMES = {PostType.CARGO: "货源大厅", PostType.CAPACITY: "运力大厅"}

# 内置驳回模板。运营选了原因但没写补充说明时用这一条，
# 而不是把「信息不真实」四个字甩给租户——那句话没有任何下一步
REJECT_TEMPLATES: Dict[int, str] = {
    PostRejectReason.INCOMPLETE: (
        "信息填得还不够全，同行看了没法判断要不要接。"
        "请补充线路、时间、台数这些关键信息后重新提交"
    ),
    PostRejectReason.UNTRUE: "这条信息和实际情况对不上，请核对后重新提交",
    PostRejectReason.CONTACT_VIOLATION: (
        "信息里写了联系方式，请删掉后重新提交。"
        "达成洽谈后系统会自动帮双方互通联系方式，不用担心联系不上"
    ),
    PostRejectReason.CARGO_NOT_SUPPORTED: (
        "这类货物需要专门资质，暂时不支持在大厅发布"
    ),
    PostRejectReason.PRICE_ABNORMAL: (
        "报价和这条线路的常见水平差得比较多，请核对后重新提交"
    ),
    PostRejectReason.DUPLICATE: (
        "你已经发过内容基本相同的信息了，重复发布会被同行当成刷屏。"
        "可以先到「我发布的」里看看已有的那条"
    ),
    PostRejectReason.ILLEGAL: "信息里有不能发布的内容，请修改后重新提交",
}

# 已经在跑成交的挂牌不能从挂牌侧下架，给运营的下一步指引
_DEAL_RUNNING_ADVICE = (
    "这条挂牌已经有成交在跑，请到成交单里走终止流程；"
    "直接下架会留下一张找不到来源的成交单"
)


@dataclass
class AuditResult:
    """单条审核动作的结果"""

    post_id: int
    post_no: str
    status: int
    audit_status: int
    message: str
    invalidated_intents: List[InvalidatedIntent] = field(default_factory=list)
    whitelist_revoked: bool = False
    # 租户侧角标是否已同步。False 表示角标暂时不准，待巡检修正，不是失败
    ref_synced: bool = True
    changed: bool = True


@dataclass
class FailedItem:
    """批量操作里没处理成功的一条"""

    post_id: int
    post_no: Optional[str]
    message: str


@dataclass
class BatchAuditResult:
    """批量通过的结果"""

    success_count: int = 0
    succeeded: List[str] = field(default_factory=list)
    failed: List[FailedItem] = field(default_factory=list)

    @property
    def message(self) -> str:
        if not self.failed:
            return f"已通过 {self.success_count} 条挂牌，它们现在都在大厅里了"
        if not self.success_count:
            return f"这 {len(self.failed)} 条都没能通过，请看下面的原因"
        return (
            f"已通过 {self.success_count} 条，"
            f"另外 {len(self.failed)} 条没能处理，请看下面的原因"
        )


class EcoAuditService:
    """运营审核"""

    # ==================================================================
    # 通过
    # ==================================================================

    @staticmethod
    async def approve(
        db: AsyncSession,
        post_id: int,
        *,
        operator: Optional[OpsContext] = None,
        remark: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> AuditResult:
        """审核通过，挂牌进入大厅"""
        now = now or datetime.now()
        post = await EcoAuditService._load(db, post_id)

        if int(post.audit_status) in AuditStatus.PASSED and int(
            post.status
        ) == PostStatus.LISTED:
            return EcoAuditService._result(
                post, message="这条挂牌已经通过审核了，正在大厅里展示", changed=False
            )
        EcoAuditService._assert_pending(post, action="通过审核")

        from_status = int(post.status)
        post.status = PostStatus.LISTED
        post.audit_status = AuditStatus.APPROVED
        post.audit_at = now
        post.audit_by = operator.user_id if operator else None
        # 上一轮的驳回理由必须清掉：这条已经通过了，租户端还挂着旧的驳回原因
        # 会让人以为又被驳了
        post.audit_reason = None
        _reslot_validity(post, now)
        if post.listed_at is None:
            post.listed_at = now
        post.last_active_at = now

        EcoAuditService._write_audit(
            db,
            post=post,
            action=PostAuditAction.APPROVE,
            from_status=from_status,
            to_status=PostStatus.LISTED,
            operator=operator,
            reason=(remark or "").strip() or "审核通过",
        )
        await db.flush()
        ref_synced = await EcoAuditService._mirror(post, PostStatus.LISTED, now)

        hall = _HALL_NAMES.get(int(post.post_type), "大厅")
        return EcoAuditService._result(
            post,
            message=f"已通过，这条挂牌现在在{hall}里了",
            ref_synced=ref_synced,
        )

    @staticmethod
    async def batch_approve(
        db: AsyncSession,
        post_ids: Sequence[int],
        *,
        operator: Optional[OpsContext] = None,
        now: Optional[datetime] = None,
    ) -> BatchAuditResult:
        """批量通过

        逐条独立 SAVEPOINT，互不牵连。返回成功数与逐条失败原因，
        让运营知道该回头处理哪几条。
        """
        now = now or datetime.now()
        ids = _dedupe(post_ids)
        if not ids:
            raise BizException("请先勾选要通过的挂牌")
        if len(ids) > MAX_BATCH_APPROVE:
            raise BizException(
                f"一次最多通过 {MAX_BATCH_APPROVE} 条，请分批处理"
            )

        post_nos = await EcoAuditService._load_post_nos(db, ids)
        result = BatchAuditResult()
        for post_id in ids:
            try:
                async with db.begin_nested():
                    one = await EcoAuditService.approve(
                        db, post_id, operator=operator, now=now
                    )
                result.success_count += 1
                result.succeeded.append(one.post_no)
            except BizException as e:
                result.failed.append(
                    FailedItem(
                        post_id=post_id,
                        post_no=post_nos.get(post_id),
                        message=str(e),
                    )
                )
            except Exception as e:  # pragma: no cover - 兜底，单条异常不拖垮整批
                logger.exception(f"[Eco] 批量通过挂牌 {post_id} 失败：{e}")
                result.failed.append(
                    FailedItem(
                        post_id=post_id,
                        post_no=post_nos.get(post_id),
                        message="这条没有处理成功，请稍后单独重试",
                    )
                )
        return result

    # ==================================================================
    # 驳回
    # ==================================================================

    @staticmethod
    async def reject(
        db: AsyncSession,
        post_id: int,
        *,
        reason_code: int,
        reason: Optional[str] = None,
        operator: Optional[OpsContext] = None,
        now: Optional[datetime] = None,
    ) -> AuditResult:
        """驳回

        **不动已有的意向。** 驳回的意思是「改改再来」，挂牌还在租户手里；
        洽谈是双方已经建立的关系，不该因为一次内容返工被单方面掐断。
        内容确实不能存在的场景走强制下架，那才是处置。
        """
        now = now or datetime.now()
        text = EcoAuditService._resolve_reject_reason(reason_code, reason)
        post = await EcoAuditService._load(db, post_id)

        if int(post.status) == PostStatus.REJECTED:
            return EcoAuditService._result(
                post, message="这条挂牌已经驳回过了", changed=False
            )
        EcoAuditService._assert_pending(post, action="驳回")

        from_status = int(post.status)
        post.status = PostStatus.REJECTED
        post.audit_status = AuditStatus.REJECTED
        post.audit_at = now
        post.audit_by = operator.user_id if operator else None
        post.audit_reason = text[:255]
        post.last_active_at = now

        EcoAuditService._write_audit(
            db,
            post=post,
            action=PostAuditAction.REJECT,
            from_status=from_status,
            to_status=PostStatus.REJECTED,
            operator=operator,
            reason=text,
            reason_code=int(reason_code),
        )
        await db.flush()
        ref_synced = await EcoAuditService._mirror(post, PostStatus.REJECTED, now)

        return EcoAuditService._result(
            post,
            message="已驳回，发布方会看到你填写的原因",
            ref_synced=ref_synced,
        )

    @staticmethod
    def _resolve_reject_reason(reason_code: int, reason: Optional[str]) -> str:
        """确定最终展示给租户的驳回原因

        必须选原因编码：只有编码才能做审核质量统计（哪类问题最多、
        该去优化哪条预检规则），自由文本统计不出来。
        没写补充说明时套用模板，但「其他」没有模板，必须自己写。
        """
        if int(reason_code) not in PostRejectReason.ALL:
            raise BizException("请选择一个驳回原因")
        text = (reason or "").strip()
        if text:
            return text
        template = REJECT_TEMPLATES.get(int(reason_code))
        if template:
            return template
        label = REJECT_REASON_LABELS.get(int(reason_code), "其他")
        raise BizException(
            f"驳回原因选了「{label}」，请补充一句说明，"
            f"发布方看到的就是这句话"
        )

    # ==================================================================
    # 强制下架
    # ==================================================================

    @staticmethod
    async def force_delist(
        db: AsyncSession,
        post_id: int,
        *,
        reason: str,
        reason_code: Optional[int] = None,
        operator: Optional[OpsContext] = None,
        revoke_whitelist: bool = True,
        now: Optional[datetime] = None,
    ) -> AuditResult:
        """强制下架

        Args:
            revoke_whitelist: 是否同时移出免审白名单。默认移出——强制下架是
                平台已经确认的违规，而白名单的含义正是「这家的内容不用看也放心」，
                两者不能同时成立。举报处置等已经单独处理过白名单的调用方传 False。
        """
        now = now or datetime.now()
        reason = (reason or "").strip()
        if not reason:
            raise BizException("请填写强制下架的原因，发布方会看到这句话")

        post = await EcoAuditService._load(db, post_id)
        if int(post.status) == PostStatus.DELISTED:
            return EcoAuditService._result(
                post, message="这条挂牌已经下架了", changed=False
            )
        return await EcoAuditService._do_force_delist(
            db,
            post=post,
            action=PostAuditAction.DELIST_FORCED,
            reason=reason,
            reason_code=reason_code,
            operator=operator,
            revoke_whitelist=revoke_whitelist,
            now=now,
            message="已强制下架，发布方会看到下架原因；正在洽谈的同行会收到通知",
        )

    # ==================================================================
    # 抽检
    # ==================================================================

    @staticmethod
    async def spot_check_pass(
        db: AsyncSession,
        post_id: int,
        *,
        operator: Optional[OpsContext] = None,
        remark: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> AuditResult:
        """抽检通过

        只改审核状态，不动挂牌状态：这条挂牌本来就在大厅里挂着，抽检通过是
        「确认可以继续挂」，不是重新上架。
        """
        now = now or datetime.now()
        post = await EcoAuditService._load(db, post_id)
        EcoAuditService._assert_spot_checkable(post)

        post.audit_status = AuditStatus.SPOT_CHECKED
        post.audit_at = now
        post.audit_by = operator.user_id if operator else None

        EcoAuditService._write_audit(
            db,
            post=post,
            action=PostAuditAction.SPOT_CHECK_PASS,
            from_status=int(post.status),
            to_status=int(post.status),
            operator=operator,
            reason=(remark or "").strip() or "抽检通过",
        )
        await db.flush()
        return EcoAuditService._result(post, message="抽检通过，已从抽检队列移出")

    @staticmethod
    async def spot_check_fail(
        db: AsyncSession,
        post_id: int,
        *,
        reason: str,
        reason_code: Optional[int] = None,
        operator: Optional[OpsContext] = None,
        now: Optional[datetime] = None,
    ) -> AuditResult:
        """抽检不通过：强制下架 + 移出免审白名单

        即使挂牌已经成交、下架、无法再撤（有成交在跑），抽检结论也要落库并
        移出白名单。免审是「先发后审」，如果「后审」查出问题却因为挂牌状态
        不合适而什么都不记，免审就变成了一条无人把守的通道。
        """
        now = now or datetime.now()
        reason = (reason or "").strip()
        if not reason:
            raise BizException("请填写抽检不通过的原因，发布方会看到这句话")

        post = await EcoAuditService._load(db, post_id)
        EcoAuditService._assert_spot_checkable(post)

        can_delist = can_transit(post.status, PostStatus.DELISTED)
        if can_delist:
            return await EcoAuditService._do_force_delist(
                db,
                post=post,
                action=PostAuditAction.SPOT_CHECK_FAIL,
                reason=reason,
                reason_code=reason_code,
                operator=operator,
                revoke_whitelist=True,
                now=now,
                message=(
                    "抽检不通过，挂牌已下架，这家企业也已移出免审白名单，"
                    "之后发布的挂牌需要人工审核"
                ),
            )

        # 撤不下来也要留痕：结论、原因、白名单处置一样都不能少
        post.audit_status = AuditStatus.REJECTED
        post.audit_at = now
        post.audit_by = operator.user_id if operator else None
        post.audit_reason = reason[:255]
        EcoAuditService._write_audit(
            db,
            post=post,
            action=PostAuditAction.SPOT_CHECK_FAIL,
            from_status=int(post.status),
            to_status=int(post.status),
            operator=operator,
            reason=reason,
            reason_code=reason_code,
        )
        await db.flush()
        revoked = await EcoAuditService._revoke_whitelist(
            db, post, reason=f"抽检不通过：{reason}", now=now
        )
        return EcoAuditService._result(
            post,
            message=(
                f"抽检结论已记录，这家企业已移出免审白名单。"
                f"这条挂牌现在是「{describe(post.status)}」，{_DEAL_RUNNING_ADVICE}"
            ),
            whitelist_revoked=revoked,
        )

    # ==================================================================
    # 共用写入
    # ==================================================================

    @staticmethod
    async def _do_force_delist(
        db: AsyncSession,
        *,
        post: SysEcoPost,
        action: int,
        reason: str,
        reason_code: Optional[int],
        operator: Optional[OpsContext],
        revoke_whitelist: bool,
        now: datetime,
        message: str,
    ) -> AuditResult:
        """强制下架与抽检不通过共用的写入

        ``audit_status`` 一并改成驳回：平台已经判定这条内容不该对外，把它留在
        「通过」或「免审直通待抽检」上，会让它继续待在抽检队列里被反复检查，
        也让租户端看不到任何审核结论。
        """
        if not can_transit(post.status, PostStatus.DELISTED):
            raise BizException(
                f"这条挂牌现在是「{describe(post.status)}」，不能下架。"
                f"{_DEAL_RUNNING_ADVICE}"
            )

        from_status = int(post.status)
        post.status = PostStatus.DELISTED
        post.audit_status = AuditStatus.REJECTED
        post.audit_at = now
        post.audit_by = operator.user_id if operator else None
        post.audit_reason = reason[:255]
        post.delist_reason = DelistReason.FORCED
        post.delist_remark = reason[:255]
        post.last_active_at = now

        invalidated = await invalidate_active_intents(
            db, post=post, reason=IntentInvalidReason.POST_DELISTED, now=now
        )
        EcoAuditService._write_audit(
            db,
            post=post,
            action=action,
            from_status=from_status,
            to_status=PostStatus.DELISTED,
            operator=operator,
            reason=reason,
            reason_code=reason_code,
        )
        await db.flush()

        revoked = False
        if revoke_whitelist:
            revoked = await EcoAuditService._revoke_whitelist(
                db, post, reason=reason, now=now
            )
        ref_synced = await EcoAuditService._mirror(post, PostStatus.DELISTED, now)

        if invalidated:
            message = (
                f"{message}（{len(invalidated)} 家正在洽谈的同行会收到通知）"
            )
        return EcoAuditService._result(
            post,
            message=message,
            invalidated_intents=invalidated,
            whitelist_revoked=revoked,
            ref_synced=ref_synced,
        )

    @staticmethod
    async def _revoke_whitelist(
        db: AsyncSession, post: SysEcoPost, *, reason: str, now: datetime
    ) -> bool:
        """移出白名单。失败不影响下架结论，只记日志

        下架已经生效了，为「白名单没摘掉」把下架一起回滚，等于让违规内容
        继续挂在大厅里。白名单的漂移由运营在白名单页手动纠正，代价小得多。
        """
        try:
            result = await EcoWhitelistService.revoke(
                db, post.owner_tenant_code, reason=reason, now=now
            )
            return result.changed
        except Exception as e:  # pragma: no cover
            logger.error(
                f"[Eco] 挂牌 {post.post_no} 处置后移出白名单失败："
                f"{post.owner_tenant_code} {e}"
            )
            return False

    @staticmethod
    async def _mirror(post: SysEcoPost, status: int, now: datetime) -> bool:
        """把状态抄回租户库镜像

        运营端没有租户库 Session，按 ``owner_tenant_code`` 临时开一个。
        注意不要在 ``async for`` 里直接 return：那样生成器不会被恢复，
        里面的 ``session.commit()`` 就不会执行，写入静默丢失。
        """
        tenant_code = post.owner_tenant_code
        if not tenant_code:
            return False
        synced = False
        try:
            async for tenant_db in db_manager.get_tenant_session(tenant_code):
                synced = await mirror_post_status(
                    tenant_db,
                    post_id=int(post.id),
                    post_no=post.post_no,
                    status=int(status),
                    now=now,
                )
        except Exception as e:
            logger.error(
                f"[Eco] 挂牌 {post.post_no} 状态回写租户库 {tenant_code} 失败，"
                f"待巡检修正：{e}"
            )
            return False
        return synced

    @staticmethod
    def _write_audit(
        db: AsyncSession,
        *,
        post: SysEcoPost,
        action: int,
        from_status: int,
        to_status: int,
        operator: Optional[OpsContext],
        reason: Optional[str] = None,
        reason_code: Optional[int] = None,
    ) -> None:
        """写流水

        ``operator_tenant_code`` 恒为空：运营不属于任何租户。想按租户统计处置
        次数要 JOIN 回挂牌表看 ``owner_tenant_code``，见
        ``audit_query_service._fill_audit_counts``。
        """
        db.add(
            SysEcoPostAudit(
                post_id=int(post.id),
                action=int(action),
                from_status=int(from_status),
                to_status=int(to_status),
                operator_type=OperatorType.PLATFORM_OPS,
                operator_id=operator.user_id if operator else None,
                operator_name=operator.user_name if operator else None,
                operator_tenant_code=None,
                reason_code=reason_code,
                reason=(reason or "")[:255] or None,
            )
        )

    # ==================================================================
    # 取数与校验
    # ==================================================================

    @staticmethod
    async def _load(db: AsyncSession, post_id: int) -> SysEcoPost:
        """按 ID 取挂牌，加行锁

        **不带租户过滤**，与租户端 ``_load_own_post`` 的差别是刻意的：
        运营的职责就是跨租户处置。加锁是因为审核是读-改-写，两个审核员同时
        点开同一条会互相覆盖结论。
        """
        post = (
            await db.execute(
                select(SysEcoPost)
                .where(SysEcoPost.id == int(post_id), SysEcoPost.is_deleted == 0)
                .with_for_update()
            )
        ).scalars().first()
        if post is None:
            raise BizException("没找到这条挂牌，它可能已经被删除了")
        return post

    @staticmethod
    async def _load_post_nos(
        db: AsyncSession, post_ids: Sequence[int]
    ) -> Dict[int, str]:
        """预取编号，让批量失败提示能说清是哪一条

        运营认的是「HY202607250012」，不是主键 ID。失败列表里只给 ID，
        运营还得回列表里一条条对，等于没告诉他。
        """
        rows = (
            await db.execute(
                select(SysEcoPost.id, SysEcoPost.post_no).where(
                    SysEcoPost.id.in_(tuple(post_ids))
                )
            )
        ).all()
        return {int(pid): no for pid, no in rows}

    @staticmethod
    def _assert_pending(post: SysEcoPost, *, action: str) -> None:
        """只有待审核队列里的挂牌才能被通过或驳回

        ``status`` 与 ``audit_status`` 都要判：只判 status 会让一条已经被
        另一个审核员处理过、状态还没刷新的挂牌被重复裁决；只判 audit_status
        会让已被强制下架的挂牌重新回到大厅。
        """
        if (
            int(post.status) == PostStatus.AUDITING
            and int(post.audit_status) == AuditStatus.PENDING
        ):
            return
        raise BizException(
            f"这条挂牌现在是「{describe(post.status)}」，不在待审核队列里，"
            f"不能{action}。刷新一下队列看看最新状态"
        )

    @staticmethod
    def _assert_spot_checkable(post: SysEcoPost) -> None:
        if int(post.audit_status) == AuditStatus.WHITELIST_PASS:
            return
        if int(post.audit_status) == AuditStatus.SPOT_CHECKED:
            raise BizException("这条挂牌已经抽检过了")
        raise BizException(
            "抽检只针对免审直通上架的挂牌，这条是人工审核通过的，不用抽检"
        )

    @staticmethod
    def _result(
        post: SysEcoPost,
        *,
        message: str,
        invalidated_intents: Optional[List[InvalidatedIntent]] = None,
        whitelist_revoked: bool = False,
        ref_synced: bool = True,
        changed: bool = True,
    ) -> AuditResult:
        return AuditResult(
            post_id=int(post.id),
            post_no=post.post_no,
            status=int(post.status),
            audit_status=int(post.audit_status),
            message=message,
            invalidated_intents=list(invalidated_intents or []),
            whitelist_revoked=whitelist_revoked,
            ref_synced=ref_synced,
            changed=changed,
        )


# ---------------------------------------------------------------------------


def _reslot_validity(post: SysEcoPost, now: datetime) -> None:
    """有效期已经过了才平移，否则不动

    挂牌在队列里排了一夜，有效期可能已经到了，直接放行等于「上架即过期」——
    大厅里看不到，租户却收到了「审核通过」。平移时保留原来的展示跨度，
    不重新给一份，避免变成一条绕开展示天数上限的路径。
    """
    if post.valid_until is None or post.valid_from is None:
        return
    if post.valid_until > now:
        return
    limit = (
        MAX_VALID_DAYS_LONG_TERM
        if int(post.cooperation_type or 0) == CooperationType.LONG_TERM
        else MAX_VALID_DAYS
    )
    span = (post.valid_until - post.valid_from).days
    if span <= 0:
        span = DEFAULT_VALID_DAYS
    post.valid_from = now
    post.valid_until = now + timedelta(days=min(span, limit))


def _dedupe(post_ids: Sequence[int]) -> List[int]:
    """去重并保持勾选顺序。顺序有意义：失败列表要按运营看到的顺序回显"""
    seen: List[int] = []
    for pid in post_ids or ():
        value = int(pid)
        if value not in seen:
            seen.append(value)
    return seen
