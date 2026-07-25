"""运营端审核取数：待审队列、抽检队列、全量检索、租户档案

对应 08.接口契约.md §4.1。与租户端的 ``post_query_service`` 是**两套不同的
安全边界**，不能互相复用：

| | 租户端大厅 | 运营端审核 |
|---|---|---|
| 可见范围 | 只看展示中、未过期、未被屏蔽的 | 全量，含草稿、驳回、过期、被屏蔽 |
| 归属过滤 | 恒带当前租户 | 不带，运营本来就要跨租户看 |
| 字段裁剪 | 按可见层级脱敏 | 不脱敏，判真伪要看原文 |

把两者写在一起，早晚会有人给大厅查询漏加一个条件，把全平台数据泄给租户。

## 租户档案为什么现算而不读 sys_eco_tenant_credit

``sys_eco_tenant_credit`` 的计数器是为「每张大厅卡片都要展示信誉」设计的，
靠事件驱动增量维护。审核台与白名单判定不一样：它们要的是**准确**而不是快，
一天跑不了几次，现算几个 COUNT 完全付得起。更关键的是，白名单准入是权限决策，
用一份可能漂移的冗余计数去决定「这家从此免审」，漂移的代价不对等。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.ecosystem.constants import (
    SPOT_CHECK_HOURS,
    WHITELIST_CLEAN_DAYS,
    AuditStatus,
    DealStatus,
    PostAuditAction,
    PostStatus,
    ReportStatus,
)
from app.modules.console.models.ecosystem.deal import SysEcoDeal
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.report import SysEcoReport
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile
from app.modules.console.services.ecosystem import audit_sla

MAX_PAGE_SIZE = 100
RECENT_POSTS_LIMIT = 5
AUDIT_TRAIL_LIMIT = 20


def _asc_nulls_first(column):
    """升序，空值排在最前（MySQL 安全写法）

    不能用 SQLAlchemy 的 ``.nulls_first()``：那是标准 SQL 语法，MySQL 不支持，
    会在运行时报语法错误。用「是否为空」作为第一排序键显式表达，
    顺带把意图写在了 SQL 里——空的进队时间意味着数据异常，该排在队首被人看见。
    """
    return (column.is_(None).desc(), column.asc())


def _desc_nulls_last(column):
    """降序，空值排在最后（MySQL 安全写法）"""
    return (column.is_(None).asc(), column.desc())


@dataclass
class OpsContext:
    """平台运营操作人

    定义在取数模块里是因为审核动作、白名单、抽检三个 Service 都要用它，
    放在其中任意一个里都会让另外两个反向依赖。
    """

    user_id: Optional[int] = None
    user_name: Optional[str] = None


@dataclass
class AuditPostFilter:
    """审核台筛选条件

    队列与全量检索共用一份：运营在队列里筛了「只看货源、只看有可疑标记的」，
    切到全量检索时希望条件还在，两套筛选结构会让这件事做不到。
    """

    post_type: Optional[int] = None
    tenant_code: Optional[str] = None
    keyword: Optional[str] = None
    # 只看预检命中可疑标记的。这是审核员最该优先看的一批
    flagged_only: bool = False
    # 只看已超出承诺时长的
    overdue_only: bool = False
    # 仅全量检索使用
    statuses: Optional[Sequence[int]] = None
    audit_statuses: Optional[Sequence[int]] = None
    submitted_from: Optional[datetime] = None
    submitted_to: Optional[datetime] = None
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return max(0, (max(1, int(self.page)) - 1) * self.limit)

    @property
    def limit(self) -> int:
        return min(MAX_PAGE_SIZE, max(1, int(self.size)))


@dataclass
class AuditQueueRow:
    """队列里的一条

    紧迫度在这里算好，而不是留给 API 层：队列排序、标红、积压告警三处都要用，
    各算一遍就会出现「列表标红了但告警没报」这种自相矛盾的现象。
    """

    post: SysEcoPost
    waited_minutes: int = 0
    urgency: int = 0
    deadline: Optional[datetime] = None

    @property
    def is_overdue(self) -> bool:
        return self.urgency == audit_sla.AuditUrgency.OVERDUE


@dataclass
class BacklogStats:
    """审核积压概览，供运营待办与看板用"""

    pending: int = 0
    pending_overdue: int = 0
    pending_flagged: int = 0
    spot_check_pending: int = 0
    spot_check_overdue: int = 0


@dataclass
class TenantAuditStats:
    """审核台右侧的租户档案（08 §4.1 ownerContext）

    审核员判断一条挂牌真不真，看内容不如看发布者：认证了没有、发过多少条、
    被驳回过几次、有没有被强制下架过。这几个数字比读三遍标题有用得多。
    """

    tenant_code: str
    tenant_name: Optional[str] = None
    masked_name: Optional[str] = None
    license_verified: bool = False
    transport_license_verified: bool = False
    realname_verified: bool = False
    hall_enabled: bool = True
    audit_whitelist: bool = False
    whitelist_source: Optional[int] = None
    whitelist_at: Optional[datetime] = None
    whitelist_revoked_at: Optional[datetime] = None
    whitelist_revoke_reason: Optional[str] = None
    publish_restricted_until: Optional[datetime] = None
    intent_restricted_until: Optional[datetime] = None

    publish_count: int = 0
    listed_count: int = 0
    pending_count: int = 0
    reject_count: int = 0
    reject_count_recent: int = 0
    force_delist_count: int = 0
    force_delist_count_recent: int = 0
    spot_check_fail_count: int = 0
    deal_count: int = 0
    deal_completed_count: int = 0
    report_valid_count: int = 0
    report_valid_count_recent: int = 0
    first_publish_at: Optional[datetime] = None
    recent_posts: List[SysEcoPost] = field(default_factory=list)

    @property
    def pass_rate(self) -> Optional[Decimal]:
        """审核通过率（%）。没发过就没有通过率，返回空而不是 0

        0% 会被读成「一次都没通过」，与「还没发过」是两件完全不同的事，
        而审核员会照着这个数字做决定。
        """
        if not self.publish_count:
            return None
        return (
            Decimal(self.listed_count) * 100 / Decimal(self.publish_count)
        ).quantize(Decimal("0.01"))


class EcoAuditQueryService:
    """审核台取数"""

    # ==================================================================
    # 队列
    # ==================================================================

    @staticmethod
    async def page_pending(
        db: AsyncSession,
        flt: Optional[AuditPostFilter] = None,
        *,
        now: Optional[datetime] = None,
    ) -> Tuple[List[AuditQueueRow], int]:
        """待人工审核队列，按进队时间正序

        正序而不是倒序：审核队列是先来先服务，倒序会让高峰期最早提交的那批
        永远排在最后，SLA 从尾部开始崩。
        """
        now = now or datetime.now()
        flt = flt or AuditPostFilter()
        stmt = EcoAuditQueryService._pending_scope(flt, now)
        total = await EcoAuditQueryService._count(db, stmt)
        rows = (
            await db.execute(
                stmt.order_by(
                    *_asc_nulls_first(SysEcoPost.submitted_at),
                    SysEcoPost.id.asc(),
                )
                .offset(flt.offset)
                .limit(flt.limit)
            )
        ).scalars().all()
        return [EcoAuditQueryService._to_row(p, now) for p in rows], total

    @staticmethod
    async def page_spot_check(
        db: AsyncSession,
        flt: Optional[AuditPostFilter] = None,
        *,
        now: Optional[datetime] = None,
    ) -> Tuple[List[AuditQueueRow], int]:
        """免审直通待抽检队列，按上架时间正序

        抽检的对象是「已经在大厅里挂着、还没有人看过」的挂牌，所以条件是
        审核状态为免审直通（抽检通过后会改成抽检通过，自然离队），
        **不限制挂牌状态**：免审直通的挂牌可能已经成交或下架了，
        它依然需要被检查——违规内容已经产生了影响，不能因为下架就免检。
        """
        now = now or datetime.now()
        flt = flt or AuditPostFilter()
        stmt = EcoAuditQueryService._spot_check_scope(flt, now)
        total = await EcoAuditQueryService._count(db, stmt)
        rows = (
            await db.execute(
                stmt.order_by(
                    *_asc_nulls_first(SysEcoPost.listed_at),
                    SysEcoPost.id.asc(),
                )
                .offset(flt.offset)
                .limit(flt.limit)
            )
        ).scalars().all()
        return [EcoAuditQueryService._to_row(p, now) for p in rows], total

    @staticmethod
    async def page_all(
        db: AsyncSession,
        flt: Optional[AuditPostFilter] = None,
        *,
        now: Optional[datetime] = None,
    ) -> Tuple[List[AuditQueueRow], int]:
        """全量检索，按进队时间倒序

        与队列相反用倒序：这里是「查一条挂牌」的场景，最近的最可能是要找的那条。
        """
        now = now or datetime.now()
        flt = flt or AuditPostFilter()
        stmt = EcoAuditQueryService._base_scope(flt, now)
        if flt.statuses:
            stmt = stmt.where(SysEcoPost.status.in_(tuple(flt.statuses)))
        if flt.audit_statuses:
            stmt = stmt.where(SysEcoPost.audit_status.in_(tuple(flt.audit_statuses)))
        total = await EcoAuditQueryService._count(db, stmt)
        rows = (
            await db.execute(
                stmt.order_by(
                    *_desc_nulls_last(SysEcoPost.submitted_at),
                    SysEcoPost.id.desc(),
                )
                .offset(flt.offset)
                .limit(flt.limit)
            )
        ).scalars().all()
        return [EcoAuditQueryService._to_row(p, now) for p in rows], total

    @staticmethod
    async def backlog_stats(
        db: AsyncSession, *, now: Optional[datetime] = None
    ) -> BacklogStats:
        """积压概览

        超时数在 SQL 里判，不是把队列全捞回来在 Python 里数：待审几万条时
        全量拉取会直接把接口拖垮。工作时段口径由 ``audit_sla.overdue_before``
        折算成一个时间界，两处判定出自同一份规则。
        """
        now = now or datetime.now()
        overdue_line = audit_sla.overdue_before(now)
        pending_where = (
            SysEcoPost.audit_status == AuditStatus.PENDING,
            SysEcoPost.status == PostStatus.AUDITING,
            SysEcoPost.is_deleted == 0,
        )
        row = (
            await db.execute(
                select(
                    func.count(),
                    func.sum(
                        case((SysEcoPost.submitted_at < overdue_line, 1), else_=0)
                    ),
                    func.sum(
                        case((SysEcoPost.precheck_flags.is_not(None), 1), else_=0)
                    ),
                )
                .select_from(SysEcoPost)
                .where(*pending_where)
            )
        ).one()

        spot_line = now - timedelta(hours=SPOT_CHECK_HOURS)
        spot = (
            await db.execute(
                select(
                    func.count(),
                    func.sum(case((SysEcoPost.listed_at < spot_line, 1), else_=0)),
                )
                .select_from(SysEcoPost)
                .where(
                    SysEcoPost.audit_status == AuditStatus.WHITELIST_PASS,
                    SysEcoPost.is_deleted == 0,
                )
            )
        ).one()

        return BacklogStats(
            pending=int(row[0] or 0),
            pending_overdue=int(row[1] or 0),
            pending_flagged=int(row[2] or 0),
            spot_check_pending=int(spot[0] or 0),
            spot_check_overdue=int(spot[1] or 0),
        )

    # ==================================================================
    # 单条与流水
    # ==================================================================

    @staticmethod
    async def get_post(db: AsyncSession, post_id: int) -> Optional[SysEcoPost]:
        """按 ID 取一条挂牌（只读，不加锁）

        与 ``EcoAuditService._load`` 的区别是不加行锁：审核详情是纯读，
        加锁会让两个审核员同时打开同一条时后一个人干等。真正的并发保护在
        动作接口那一侧。
        """
        return (
            await db.execute(
                select(SysEcoPost).where(
                    SysEcoPost.id == int(post_id), SysEcoPost.is_deleted == 0
                )
            )
        ).scalars().first()

    @staticmethod
    async def load_audit_trail(
        db: AsyncSession, post_id: int, *, limit: int = AUDIT_TRAIL_LIMIT
    ) -> List[SysEcoPostAudit]:
        """挂牌的流转流水，最近在前

        审核员这一轮要看什么，取决于上一轮为什么驳回、租户之后改了哪些字段。
        没有流水就只能凭标题重审一遍，同一个问题会被反复发现。
        """
        return list(
            (
                await db.execute(
                    select(SysEcoPostAudit)
                    .where(
                        SysEcoPostAudit.post_id == int(post_id),
                        SysEcoPostAudit.is_deleted == 0,
                    )
                    .order_by(SysEcoPostAudit.id.desc())
                    .limit(max(1, int(limit)))
                )
            ).scalars().all()
        )

    # ==================================================================
    # 租户档案
    # ==================================================================

    @staticmethod
    async def load_tenant_stats(
        db: AsyncSession,
        tenant_code: str,
        *,
        now: Optional[datetime] = None,
        exclude_post_id: Optional[int] = None,
        with_recent_posts: bool = True,
    ) -> TenantAuditStats:
        """租户在服务平台的完整档案（现算）"""
        now = now or datetime.now()
        since = now - timedelta(days=WHITELIST_CLEAN_DAYS)
        stats = TenantAuditStats(tenant_code=tenant_code)

        await EcoAuditQueryService._fill_profile(db, stats)
        await EcoAuditQueryService._fill_post_counts(db, stats)
        await EcoAuditQueryService._fill_audit_counts(db, stats, since)
        await EcoAuditQueryService._fill_deal_counts(db, stats)
        await EcoAuditQueryService._fill_report_counts(db, stats, since)
        if with_recent_posts:
            stats.recent_posts = await EcoAuditQueryService._recent_posts(
                db, tenant_code, exclude_post_id
            )
        return stats

    @staticmethod
    async def _fill_profile(db: AsyncSession, stats: TenantAuditStats) -> None:
        """名片与信誉表里的「配置类」字段照读

        认证状态、大厅开关、白名单标记是运营写进去的事实，不是统计出来的，
        没有现算的必要，也没有漂移的可能。
        """
        profile = (
            await db.execute(
                select(SysEcoTenantProfile).where(
                    SysEcoTenantProfile.tenant_code == stats.tenant_code,
                    SysEcoTenantProfile.is_deleted == 0,
                )
            )
        ).scalars().first()
        if profile is not None:
            stats.tenant_name = profile.display_name
            stats.masked_name = profile.masked_name
            stats.license_verified = int(profile.license_verified or 0) == 1
            stats.transport_license_verified = (
                int(profile.transport_license_verified or 0) == 1
            )
            stats.realname_verified = int(profile.realname_verified or 0) == 1
            stats.hall_enabled = int(profile.hall_enabled or 0) == 1

        credit = (
            await db.execute(
                select(SysEcoTenantCredit).where(
                    SysEcoTenantCredit.tenant_code == stats.tenant_code,
                    SysEcoTenantCredit.is_deleted == 0,
                )
            )
        ).scalars().first()
        if credit is not None:
            stats.audit_whitelist = int(credit.audit_whitelist or 0) == 1
            stats.whitelist_source = credit.whitelist_source
            stats.whitelist_at = credit.whitelist_at
            stats.whitelist_revoked_at = credit.whitelist_revoked_at
            stats.whitelist_revoke_reason = credit.whitelist_revoke_reason
            stats.publish_restricted_until = credit.publish_restricted_until
            stats.intent_restricted_until = credit.intent_restricted_until

    @staticmethod
    async def _fill_post_counts(db: AsyncSession, stats: TenantAuditStats) -> None:
        """发布量口径

        ``listed_count`` 数的是 ``listed_at IS NOT NULL``（曾经上架过），
        不是「当前状态为展示中」：后者会把已成交、已到期的挂牌算成没通过审核，
        通过率于是随时间自己往下掉。
        """
        row = (
            await db.execute(
                select(
                    func.count(),
                    func.sum(case((SysEcoPost.listed_at.is_not(None), 1), else_=0)),
                    func.sum(
                        case(
                            (SysEcoPost.audit_status == AuditStatus.PENDING, 1),
                            else_=0,
                        )
                    ),
                    func.min(SysEcoPost.created_at),
                )
                .select_from(SysEcoPost)
                .where(
                    SysEcoPost.owner_tenant_code == stats.tenant_code,
                    SysEcoPost.audit_status != AuditStatus.NOT_SUBMITTED,
                    SysEcoPost.is_deleted == 0,
                )
            )
        ).one()
        stats.publish_count = int(row[0] or 0)
        stats.listed_count = int(row[1] or 0)
        stats.pending_count = int(row[2] or 0)
        stats.first_publish_at = row[3]

    @staticmethod
    async def _fill_audit_counts(
        db: AsyncSession, stats: TenantAuditStats, since: datetime
    ) -> None:
        """驳回、强制下架、抽检不通过的次数

        必须 JOIN 回挂牌表按 ``owner_tenant_code`` 过滤：运营操作的流水行上
        ``operator_tenant_code`` 是空的（操作人不属于任何租户），
        照它过滤会把所有运营处置漏掉，档案上永远显示「零违规」。
        """
        actions = (
            PostAuditAction.REJECT,
            PostAuditAction.DELIST_FORCED,
            PostAuditAction.SPOT_CHECK_FAIL,
        )
        rows = (
            await db.execute(
                select(
                    SysEcoPostAudit.action,
                    func.count(),
                    func.sum(
                        case((SysEcoPostAudit.created_at >= since, 1), else_=0)
                    ),
                )
                .select_from(SysEcoPostAudit)
                .join(SysEcoPost, SysEcoPost.id == SysEcoPostAudit.post_id)
                .where(
                    SysEcoPost.owner_tenant_code == stats.tenant_code,
                    SysEcoPostAudit.action.in_(actions),
                    SysEcoPostAudit.is_deleted == 0,
                    SysEcoPost.is_deleted == 0,
                )
                .group_by(SysEcoPostAudit.action)
            )
        ).all()
        for action, total, recent in rows:
            total, recent = int(total or 0), int(recent or 0)
            if int(action) == PostAuditAction.REJECT:
                stats.reject_count = total
                stats.reject_count_recent = recent
            elif int(action) == PostAuditAction.DELIST_FORCED:
                stats.force_delist_count = total
                stats.force_delist_count_recent = recent
            else:
                stats.spot_check_fail_count = total

    @staticmethod
    async def _fill_deal_counts(db: AsyncSession, stats: TenantAuditStats) -> None:
        """成交量，挂牌方与合作方两侧都算

        白名单条件里的「累计成交 ≥ 1 单且完成」不区分这家是出货的还是拉货的，
        只区分他有没有真的把一单合作做完。
        """
        row = (
            await db.execute(
                select(
                    func.count(),
                    func.sum(
                        case((SysEcoDeal.status == DealStatus.COMPLETED, 1), else_=0)
                    ),
                )
                .select_from(SysEcoDeal)
                .where(
                    or_(
                        SysEcoDeal.owner_tenant_code == stats.tenant_code,
                        SysEcoDeal.partner_tenant_code == stats.tenant_code,
                    ),
                    SysEcoDeal.is_deleted == 0,
                )
            )
        ).one()
        stats.deal_count = int(row[0] or 0)
        stats.deal_completed_count = int(row[1] or 0)

    @staticmethod
    async def _fill_report_counts(
        db: AsyncSession, stats: TenantAuditStats, since: datetime
    ) -> None:
        """被举报且成立的次数。不成立与证据不足的不算，那不是违规记录"""
        row = (
            await db.execute(
                select(
                    func.count(),
                    func.sum(
                        case(
                            (
                                func.coalesce(
                                    SysEcoReport.handle_at, SysEcoReport.created_at
                                )
                                >= since,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                )
                .select_from(SysEcoReport)
                .where(
                    SysEcoReport.reported_tenant_code == stats.tenant_code,
                    SysEcoReport.status == ReportStatus.VALID,
                    SysEcoReport.is_deleted == 0,
                )
            )
        ).one()
        stats.report_valid_count = int(row[0] or 0)
        stats.report_valid_count_recent = int(row[1] or 0)

    @staticmethod
    async def _recent_posts(
        db: AsyncSession, tenant_code: str, exclude_post_id: Optional[int]
    ) -> List[SysEcoPost]:
        """该租户最近几条挂牌，给审核员做同租户横向比对（识别刷屏）"""
        stmt = select(SysEcoPost).where(
            SysEcoPost.owner_tenant_code == tenant_code,
            SysEcoPost.audit_status != AuditStatus.NOT_SUBMITTED,
            SysEcoPost.is_deleted == 0,
        )
        if exclude_post_id:
            stmt = stmt.where(SysEcoPost.id != int(exclude_post_id))
        return list(
            (
                await db.execute(
                    stmt.order_by(SysEcoPost.created_at.desc()).limit(
                        RECENT_POSTS_LIMIT
                    )
                )
            ).scalars().all()
        )

    # ==================================================================
    # 查询范围
    # ==================================================================

    @staticmethod
    def _base_scope(flt: AuditPostFilter, now: datetime) -> Select:
        """公共条件

        只有 ``is_deleted = 0`` 是恒定条件。**不带任何归属或可见性过滤**——
        运营审核就是要看全量，包括被租户屏蔽名单挡住的、已过期的、被下架的。
        """
        stmt = select(SysEcoPost).where(SysEcoPost.is_deleted == 0)
        if flt.post_type:
            stmt = stmt.where(SysEcoPost.post_type == int(flt.post_type))
        if flt.tenant_code:
            stmt = stmt.where(SysEcoPost.owner_tenant_code == flt.tenant_code)
        if flt.keyword:
            kw = f"%{flt.keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    SysEcoPost.post_no.like(kw),
                    SysEcoPost.title.like(kw),
                    SysEcoPost.owner_tenant_name.like(kw),
                )
            )
        if flt.flagged_only:
            # 预检没命中时写的是 NULL（``list(...) or None``），不是 ``[]``，
            # 所以判空即可，不需要再算 JSON 长度
            stmt = stmt.where(SysEcoPost.precheck_flags.is_not(None))
        if flt.overdue_only:
            stmt = stmt.where(SysEcoPost.submitted_at < audit_sla.overdue_before(now))
        if flt.submitted_from:
            stmt = stmt.where(SysEcoPost.submitted_at >= flt.submitted_from)
        if flt.submitted_to:
            stmt = stmt.where(SysEcoPost.submitted_at <= flt.submitted_to)
        return stmt

    @staticmethod
    def _pending_scope(flt: AuditPostFilter, now: datetime) -> Select:
        """待审：审核状态待审 且 挂牌状态待审核

        两个条件都要：只判 ``audit_status`` 会把「已被强制下架但审核状态还没
        被改写」的脏数据留在队列里，审核员点通过会把一条已下架的挂牌重新推上去。
        """
        return EcoAuditQueryService._base_scope(flt, now).where(
            SysEcoPost.audit_status == AuditStatus.PENDING,
            SysEcoPost.status == PostStatus.AUDITING,
        )

    @staticmethod
    def _spot_check_scope(flt: AuditPostFilter, now: datetime) -> Select:
        return EcoAuditQueryService._base_scope(flt, now).where(
            SysEcoPost.audit_status == AuditStatus.WHITELIST_PASS
        )

    # ==================================================================
    # 工具
    # ==================================================================

    @staticmethod
    async def _count(db: AsyncSession, stmt: Select) -> int:
        return int(
            (
                await db.execute(
                    select(func.count()).select_from(stmt.subquery())
                )
            ).scalar()
            or 0
        )

    @staticmethod
    def _to_row(post: SysEcoPost, now: datetime) -> AuditQueueRow:
        submitted = post.submitted_at or post.created_at
        if submitted is None:
            return AuditQueueRow(post=post)
        return AuditQueueRow(
            post=post,
            waited_minutes=audit_sla.waited_minutes(submitted, now),
            urgency=audit_sla.urgency(submitted, now),
            deadline=audit_sla.sla_deadline(submitted),
        )
