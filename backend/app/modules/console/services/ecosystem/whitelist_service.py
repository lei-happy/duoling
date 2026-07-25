"""免审白名单：资格判定与授予 / 移出

对应 04.运营审核与风控设计.md §2.2。白名单是整个审核体系里性价比最高的设计：
老用户占了大部分发布量，把他们放行，人工审核的压力立刻降到可控范围，
同时老用户拿到了「我是可信商家」的正反馈。

## 判定结果为什么要逐条返回

运营在审核台上最常问的一句是「这家为什么还没进白名单」。只回一个
``eligible: false`` 等于没回答，运营只能挨个字段去核对。逐条返回每个条件的
通过情况与差距（还差几条挂牌、还差多少天），这个问题就自己回答了。

## 人工授予能免掉什么、免不掉什么

| 条件 | 自动授予 | 人工授予 |
|------|---------|---------|
| 企业认证、大厅能力正常 | 必须满足 | **同样必须满足** |
| 发布量、成交量、干净期 | 必须满足 | 可由运营酌情放行 |

认证不能免：`04` §5.1 明确「认证是参与大厅的前提」，一个未核验营业执照的租户
免审直通，等于平台把最基本的身份门槛也让掉了。发布量与成交量可以免：
运营线下认识这家企业、或者刚签的重点客户，这类判断本来就该由人来做。

## 审计

授予 / 移出的当前状态与操作人记在 ``sys_eco_tenant_credit`` 上，
完整操作历史由 API 层的 ``@operation_log`` 落到 ``sys_operation_log``，
本模块不再自建一张流水表。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.ecosystem.constants import (
    WHITELIST_CLEAN_DAYS,
    WHITELIST_MIN_DEAL,
    WHITELIST_MIN_PUBLISH,
    WHITELIST_RECOVER_DAYS,
    WhitelistSource,
)
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile
from app.modules.console.services.ecosystem.audit_query_service import (
    EcoAuditQueryService,
    OpsContext,
    TenantAuditStats,
)


class WhitelistCheck:
    """资格条件编码"""

    HALL_ENABLED = "hall_enabled"
    LICENSE_VERIFIED = "license_verified"
    PUBLISH_VOLUME = "publish_volume"
    NO_REJECT = "no_reject"
    DEAL_RECORD = "deal_record"
    NO_VIOLATION = "no_violation"
    RECOVER_PERIOD = "recover_period"


@dataclass
class CheckItem:
    """一条资格条件的判定结果"""

    code: str
    label: str
    passed: bool
    detail: str
    # 人工授予也不能放行的硬条件
    blocking: bool = False


@dataclass
class EligibilityResult:
    """资格判定结果"""

    tenant_code: str
    items: List[CheckItem] = field(default_factory=list)

    @property
    def eligible(self) -> bool:
        """是否满足自动授予的全部条件"""
        return all(i.passed for i in self.items)

    @property
    def manual_allowed(self) -> bool:
        """是否允许运营人工授予"""
        return all(i.passed for i in self.items if i.blocking)

    @property
    def unmet(self) -> List[CheckItem]:
        return [i for i in self.items if not i.passed]

    @property
    def summary(self) -> str:
        """一句话说清差在哪儿，直接可以展示给运营"""
        if self.eligible:
            return "已满足免审白名单的全部条件"
        return "；".join(i.detail for i in self.unmet)


@dataclass
class WhitelistResult:
    """授予 / 移出的结果"""

    tenant_code: str
    audit_whitelist: bool
    message: str
    source: Optional[int] = None
    changed: bool = True


class EcoWhitelistService:
    """免审白名单"""

    # ==================================================================
    # 资格判定
    # ==================================================================

    @staticmethod
    async def evaluate(
        db: AsyncSession,
        tenant_code: str,
        *,
        now: Optional[datetime] = None,
        stats: Optional[TenantAuditStats] = None,
    ) -> EligibilityResult:
        """判定一个租户是否够资格免审

        Args:
            stats: 已经取过的租户档案。审核详情页本来就要展示档案，
                复用它可以省掉一整轮聚合查询。
        """
        now = now or datetime.now()
        if stats is None:
            stats = await EcoAuditQueryService.load_tenant_stats(
                db, tenant_code, now=now, with_recent_posts=False
            )
        return EligibilityResult(
            tenant_code=tenant_code,
            items=[
                EcoWhitelistService._check_hall(stats),
                EcoWhitelistService._check_license(stats),
                EcoWhitelistService._check_publish(stats),
                EcoWhitelistService._check_reject(stats),
                EcoWhitelistService._check_deal(stats),
                EcoWhitelistService._check_violation(stats),
                EcoWhitelistService._check_recover(stats, now),
            ],
        )

    @staticmethod
    def _check_hall(stats: TenantAuditStats) -> CheckItem:
        return CheckItem(
            code=WhitelistCheck.HALL_ENABLED,
            label="大厅能力",
            passed=stats.hall_enabled,
            detail=(
                "大厅能力正常"
                if stats.hall_enabled
                else "大厅能力已被关停，先恢复能力再谈免审"
            ),
            blocking=True,
        )

    @staticmethod
    def _check_license(stats: TenantAuditStats) -> CheckItem:
        return CheckItem(
            code=WhitelistCheck.LICENSE_VERIFIED,
            label="企业认证",
            passed=stats.license_verified,
            detail=(
                "已通过营业执照核验"
                if stats.license_verified
                else "营业执照还没核验，认证是参与大厅的前提，不能免"
            ),
            blocking=True,
        )

    @staticmethod
    def _check_publish(stats: TenantAuditStats) -> CheckItem:
        passed = stats.publish_count >= WHITELIST_MIN_PUBLISH
        gap = WHITELIST_MIN_PUBLISH - stats.publish_count
        return CheckItem(
            code=WhitelistCheck.PUBLISH_VOLUME,
            label="历史挂牌",
            passed=passed,
            detail=(
                f"累计发布 {stats.publish_count} 条"
                if passed
                else f"累计发布 {stats.publish_count} 条，还差 {gap} 条"
            ),
        )

    @staticmethod
    def _check_reject(stats: TenantAuditStats) -> CheckItem:
        """驳回记录按近 90 天回溯，不看历史全量

        文档原文是「全部审核通过」，这里刻意收窄到 90 天窗口：一次一年前的
        驳回永久堵住免审通道，和文档自己定的「移出后重新累积 30 天即可再进」
        是互相矛盾的两套尺度——那条规则已经确认了处置应该随时间衰减。
        """
        passed = stats.reject_count_recent == 0
        return CheckItem(
            code=WhitelistCheck.NO_REJECT,
            label="审核记录",
            passed=passed,
            detail=(
                f"近 {WHITELIST_CLEAN_DAYS} 天没有被驳回过"
                if passed
                else f"近 {WHITELIST_CLEAN_DAYS} 天被驳回过 "
                     f"{stats.reject_count_recent} 次"
            ),
        )

    @staticmethod
    def _check_deal(stats: TenantAuditStats) -> CheckItem:
        passed = stats.deal_completed_count >= WHITELIST_MIN_DEAL
        return CheckItem(
            code=WhitelistCheck.DEAL_RECORD,
            label="成交记录",
            passed=passed,
            detail=(
                f"已完成 {stats.deal_completed_count} 单合作"
                if passed
                else "还没有完成过一单合作"
            ),
        )

    @staticmethod
    def _check_violation(stats: TenantAuditStats) -> CheckItem:
        forced = stats.force_delist_count_recent
        reported = stats.report_valid_count_recent
        passed = forced == 0 and reported == 0
        if passed:
            detail = f"近 {WHITELIST_CLEAN_DAYS} 天没有违规记录"
        else:
            parts = []
            if forced:
                parts.append(f"被强制下架 {forced} 次")
            if reported:
                parts.append(f"被举报成立 {reported} 次")
            detail = f"近 {WHITELIST_CLEAN_DAYS} 天" + "、".join(parts)
        return CheckItem(
            code=WhitelistCheck.NO_VIOLATION,
            label="违规记录",
            passed=passed,
            detail=detail,
        )

    @staticmethod
    def _check_recover(stats: TenantAuditStats, now: datetime) -> CheckItem:
        """被移出后的冷静期"""
        revoked_at = stats.whitelist_revoked_at
        if revoked_at is None:
            return CheckItem(
                code=WhitelistCheck.RECOVER_PERIOD,
                label="冷静期",
                passed=True,
                detail="没有被移出过白名单",
            )
        recover_at = revoked_at + timedelta(days=WHITELIST_RECOVER_DAYS)
        passed = now >= recover_at
        return CheckItem(
            code=WhitelistCheck.RECOVER_PERIOD,
            label="冷静期",
            passed=passed,
            detail=(
                f"已过 {WHITELIST_RECOVER_DAYS} 天冷静期"
                if passed
                else f"{revoked_at:%Y-%m-%d} 被移出过，"
                     f"{recover_at:%Y-%m-%d} 之后才能重新进入"
            ),
        )

    # ==================================================================
    # 授予与移出
    # ==================================================================

    @staticmethod
    async def grant(
        db: AsyncSession,
        tenant_code: str,
        *,
        operator: Optional[OpsContext] = None,
        source: int = WhitelistSource.MANUAL,
        now: Optional[datetime] = None,
    ) -> WhitelistResult:
        """加入免审白名单

        自动授予（``source=AUTO``）要求全部条件满足；人工授予只要求硬条件满足，
        其余由运营判断。不满足硬条件时抛业务异常，把差在哪儿直接说清。
        """
        now = now or datetime.now()
        credit = await EcoWhitelistService._load_or_create(db, tenant_code)
        if int(credit.audit_whitelist or 0) == 1:
            return WhitelistResult(
                tenant_code=tenant_code,
                audit_whitelist=True,
                message="这家企业已经在免审白名单里了",
                source=credit.whitelist_source,
                changed=False,
            )

        result = await EcoWhitelistService.evaluate(db, tenant_code, now=now)
        if int(source) == WhitelistSource.AUTO:
            if not result.eligible:
                raise BizException(f"还不满足免审条件：{result.summary}")
        elif not result.manual_allowed:
            raise BizException(f"这家企业暂时不能免审：{result.summary}")

        credit.audit_whitelist = 1
        credit.whitelist_at = now
        credit.whitelist_by = operator.user_id if operator else None
        credit.whitelist_source = int(source)
        # 移出记录留着：进出白名单的历史比当前状态更能说明这家企业的稳定性，
        # 冷静期也要靠它计算
        await db.flush()

        return WhitelistResult(
            tenant_code=tenant_code,
            audit_whitelist=True,
            message="已加入免审白名单，之后发布的挂牌会直接上架并进入抽检队列",
            source=int(source),
        )

    @staticmethod
    async def revoke(
        db: AsyncSession,
        tenant_code: str,
        *,
        reason: str,
        operator: Optional[OpsContext] = None,
        now: Optional[datetime] = None,
    ) -> WhitelistResult:
        """移出免审白名单

        ``reason`` 必填。抽检不通过、举报成立、连续爽约三条触发路径都会走到这里，
        不记原因的话，30 天后运营看到一条「曾被移出」却不知道当初发生了什么，
        既无法判断该不该恢复，也无法向租户解释。
        """
        now = now or datetime.now()
        reason = (reason or "").strip()
        if not reason:
            raise BizException("请填写移出白名单的原因，之后恢复时需要参考")

        credit = await EcoWhitelistService._load_or_create(db, tenant_code)
        already_out = int(credit.audit_whitelist or 0) == 0
        credit.audit_whitelist = 0
        credit.whitelist_source = None
        credit.whitelist_revoked_at = now
        credit.whitelist_revoke_reason = reason[:255]
        await db.flush()

        return WhitelistResult(
            tenant_code=tenant_code,
            audit_whitelist=False,
            message=(
                "这家企业本来就不在免审白名单里，已记录本次处置"
                if already_out
                else f"已移出免审白名单，{WHITELIST_RECOVER_DAYS} 天内不会自动恢复"
            ),
            changed=not already_out,
        )

    @staticmethod
    async def sync_auto(
        db: AsyncSession,
        tenant_code: str,
        *,
        now: Optional[datetime] = None,
    ) -> WhitelistResult:
        """自动授予的入口（供成交完成事件与每日校准 Worker 调用）

        只做「不够资格 → 什么都不做」和「够资格 → 授予」两件事，
        **不做自动移出**。移出是处置动作，必须有明确的触发事件与原因
        （抽检不通过、举报成立、爽约），由那些路径显式调用 ``revoke``；
        让定时任务按条件反推着摘牌，租户会在毫无提示的情况下失去免审，
        运营也查不到是谁摘的。
        """
        now = now or datetime.now()
        credit = await EcoWhitelistService._load_or_create(db, tenant_code)
        if int(credit.audit_whitelist or 0) == 1:
            return WhitelistResult(
                tenant_code=tenant_code,
                audit_whitelist=True,
                message="已在免审白名单里",
                source=credit.whitelist_source,
                changed=False,
            )

        result = await EcoWhitelistService.evaluate(db, tenant_code, now=now)
        if not result.eligible:
            return WhitelistResult(
                tenant_code=tenant_code,
                audit_whitelist=False,
                message=result.summary,
                changed=False,
            )
        return await EcoWhitelistService.grant(
            db, tenant_code, source=WhitelistSource.AUTO, now=now
        )

    # ==================================================================
    # 取数
    # ==================================================================

    @staticmethod
    async def page_members(
        db: AsyncSession,
        *,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Tuple[SysEcoTenantCredit, Optional[str]]], int]:
        """白名单成员分页

        左连名片表取企业名：信誉表里只有 ``tenant_code``，运营认的是企业名称。
        用 outer join 而不是 inner join，是因为名片表理论上可能缺行
        （懒加载创建），inner join 会让这家企业从白名单列表里凭空消失——
        而它依然享受免审，看不见比看得见危险得多。
        """
        stmt = (
            select(SysEcoTenantCredit, SysEcoTenantProfile.display_name)
            .outerjoin(
                SysEcoTenantProfile,
                SysEcoTenantProfile.tenant_code == SysEcoTenantCredit.tenant_code,
            )
            .where(
                SysEcoTenantCredit.audit_whitelist == 1,
                SysEcoTenantCredit.is_deleted == 0,
            )
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    SysEcoTenantCredit.tenant_code.like(kw),
                    SysEcoTenantProfile.display_name.like(kw),
                )
            )

        total = int(
            (
                await db.execute(select(func.count()).select_from(stmt.subquery()))
            ).scalar()
            or 0
        )
        limit = min(100, max(1, int(size)))
        rows = (
            await db.execute(
                stmt.order_by(SysEcoTenantCredit.whitelist_at.desc())
                .offset(max(0, (max(1, int(page)) - 1) * limit))
                .limit(limit)
            )
        ).all()
        return [(credit, name) for credit, name in rows], total

    @staticmethod
    async def _load_or_create(
        db: AsyncSession, tenant_code: str
    ) -> SysEcoTenantCredit:
        """取信誉记录，没有就建

        ``sys_eco_tenant_credit`` 是懒加载创建的（多数租户不会碰服务平台，
        预生成几千条空记录会让运营指标失真）。白名单操作是它的第一个写入方，
        所以取不到就在这里补建，而不是报「这家企业没有信誉记录」——
        那对运营来说是一句没有下一步的错误。
        """
        if not tenant_code:
            raise BizException("请选择要操作的企业")
        credit = (
            await db.execute(
                select(SysEcoTenantCredit)
                .where(
                    SysEcoTenantCredit.tenant_code == tenant_code,
                    SysEcoTenantCredit.is_deleted == 0,
                )
                .with_for_update()
            )
        ).scalars().first()
        if credit is None:
            credit = SysEcoTenantCredit(tenant_code=tenant_code)
            db.add(credit)
            await db.flush()
        return credit
