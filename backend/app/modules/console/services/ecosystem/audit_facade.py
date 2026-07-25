"""审核台读接口的装配层（读平台库）

把「取数 → 批量装载关联 → 序列化」这三步收在一处，API 层只负责翻译入参。
与租户端 ``EcoHallFacade`` 同构，但两者的取数与序列化各用自己那一套
（原因见 ``audit_query_service`` 与 ``audit_serializer`` 的模块注释）。

## 审核详情为什么要一次给全

审核员的判断依据分散在四处：挂牌内容、预检标记、发布方历史、源单核验。
分成四个接口，界面上就是四次请求四个 loading，审核员在等待里失去节奏；
更糟的是任何一个请求失败，他会在信息不全的情况下点通过。
一次给全，慢 50 毫秒，但结论是完整的。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.services.ecosystem.post_query_service import (
    EcoPostQueryService,
)
from app.modules.console.models.ecosystem.constants import PostType
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.services.ecosystem.audit_query_service import (
    AuditPostFilter,
    AuditQueueRow,
    EcoAuditQueryService,
)
from app.modules.console.services.ecosystem.audit_serializer import EcoAuditSerializer
from app.modules.console.services.ecosystem.whitelist_service import (
    EcoWhitelistService,
)


class EcoAuditFacade:
    """审核台读接口装配"""

    # ------------------------------------------------------------------
    # 队列
    # ------------------------------------------------------------------

    @staticmethod
    async def page_pending(
        db: AsyncSession, flt: AuditPostFilter, *, now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        rows, total = await EcoAuditQueryService.page_pending(db, flt, now=now)
        return EcoAuditFacade._page(rows, total, flt)

    @staticmethod
    async def page_spot_check(
        db: AsyncSession, flt: AuditPostFilter, *, now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        rows, total = await EcoAuditQueryService.page_spot_check(db, flt, now=now)
        return EcoAuditFacade._page(rows, total, flt)

    @staticmethod
    async def page_all(
        db: AsyncSession, flt: AuditPostFilter, *, now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        rows, total = await EcoAuditQueryService.page_all(db, flt, now=now)
        return EcoAuditFacade._page(rows, total, flt)

    @staticmethod
    def _page(
        rows: Sequence[AuditQueueRow], total: int, flt: AuditPostFilter
    ) -> Dict[str, Any]:
        return {
            "list": [EcoAuditSerializer.queue_row(r) for r in rows],
            "total": total,
            "count": total,
            "page": flt.page,
            "pageSize": flt.limit,
        }

    @staticmethod
    async def backlog(
        db: AsyncSession, *, now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        return EcoAuditSerializer.backlog(
            await EcoAuditQueryService.backlog_stats(db, now=now)
        )

    # ------------------------------------------------------------------
    # 审核详情
    # ------------------------------------------------------------------

    @staticmethod
    async def detail(
        db: AsyncSession, post_id: int, *, now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """审核详情：挂牌全字段 + 预检 + 源单核验 + 发布方档案 + 流水 + 白名单资格"""
        now = now or datetime.now()
        post = await EcoAuditQueryService.get_post(db, post_id)
        if post is None:
            raise BizException("没找到这条挂牌，它可能已经被删除了")

        post_type = int(post.post_type)
        related = await EcoPostQueryService.load_related(db, [post], post_type)
        ext = related["ext"].get(post.id)

        stats = await EcoAuditQueryService.load_tenant_stats(
            db, post.owner_tenant_code, now=now, exclude_post_id=int(post.id)
        )
        # 档案已经取过了，资格判定复用它，省掉一整轮聚合查询
        eligibility = await EcoWhitelistService.evaluate(
            db, post.owner_tenant_code, now=now, stats=stats
        )
        trail = await EcoAuditQueryService.load_audit_trail(db, int(post.id))

        return {
            "post": EcoAuditSerializer.post_full(
                post,
                cargo=ext if post_type == PostType.CARGO else None,
                capacity=ext if post_type != PostType.CARGO else None,
                destinations=related["dests"].get(post.id, []),
            ),
            "precheck": EcoAuditSerializer.precheck(post),
            "sourceCheck": EcoAuditSerializer.source_check(post),
            "ownerContext": EcoAuditSerializer.tenant_context(stats),
            "whitelistEligibility": EcoAuditSerializer.eligibility(eligibility),
            "auditTrail": EcoAuditSerializer.audit_trail(trail),
            "sla": EcoAuditFacade._sla(post, now),
        }

    @staticmethod
    def _sla(post: SysEcoPost, now: datetime) -> Optional[Dict[str, Any]]:
        """详情页顶部的时效提示

        复用队列行的口径（``_to_row``），保证详情页显示的等待时长与队列里
        看到的完全一致——两处不一致时，审核员会怀疑哪个数是对的。
        """
        row = EcoAuditQueryService._to_row(post, now)
        data = EcoAuditSerializer.queue_row(row)
        data.pop("post", None)
        return data

    # ------------------------------------------------------------------
    # 租户档案与白名单
    # ------------------------------------------------------------------

    @staticmethod
    async def tenant_profile(
        db: AsyncSession, tenant_code: str, *, now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """租户在服务平台的档案 + 白名单资格

        白名单页与审核详情页问的是同一个问题「这家企业靠不靠得住」，
        所以给同一份数据结构，前端两处可以共用一个组件。
        """
        now = now or datetime.now()
        stats = await EcoAuditQueryService.load_tenant_stats(
            db, tenant_code, now=now
        )
        eligibility = await EcoWhitelistService.evaluate(
            db, tenant_code, now=now, stats=stats
        )
        return {
            "tenant": EcoAuditSerializer.tenant_context(stats),
            "eligibility": EcoAuditSerializer.eligibility(eligibility),
        }

    @staticmethod
    async def page_whitelist(
        db: AsyncSession,
        *,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        rows, total = await EcoWhitelistService.page_members(
            db, keyword=keyword, page=page, size=size
        )
        return {
            "list": [EcoAuditSerializer.whitelist_member(r) for r in rows],
            "total": total,
            "count": total,
            "page": page,
            "pageSize": size,
        }
