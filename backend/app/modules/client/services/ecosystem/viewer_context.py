"""服务平台查看方上下文构建（读平台库）

把「查看方是谁、认证了没、跟哪些挂牌在洽谈/已成交」一次性查出来，交给
纯逻辑的可见性内核使用。

**列表页必须走批量接口**（``build_for_posts``）：如果对每条挂牌单独查一次
洽谈关系，20 条卡片就是 40 次查询。这里用两条 IN 查询解决整页。
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.services.ecosystem.visibility import EcoViewerContext
from app.modules.console.models.ecosystem.constants import DealStatus, IntentStatus
from app.modules.console.models.ecosystem.deal import SysEcoDeal
from app.modules.console.models.ecosystem.intent import SysEcoIntent
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile


class EcoViewerContextBuilder:
    """构建 ``EcoViewerContext``"""

    @staticmethod
    async def is_license_verified(db: AsyncSession, tenant_code: str) -> bool:
        """租户是否已完成营业执照核验（决定 L1/L2）

        名片表是懒加载的，查不到记录等同于未核验——**不能因为记录缺失就放宽**。
        """
        result = await db.execute(
            select(SysEcoTenantProfile.license_verified).where(
                SysEcoTenantProfile.tenant_code == tenant_code,
                SysEcoTenantProfile.is_deleted == 0,
            )
        )
        return int(result.scalar() or 0) == 1

    @staticmethod
    async def build_for_posts(
        db: AsyncSession,
        viewer_tenant_code: str,
        post_ids: Sequence[int],
        *,
        license_verified: Optional[bool] = None,
        is_platform_ops: bool = False,
    ) -> EcoViewerContext:
        """为一批挂牌构建上下文（列表页与详情页共用）"""
        if license_verified is None:
            license_verified = await EcoViewerContextBuilder.is_license_verified(
                db, viewer_tenant_code
            )

        negotiating: Set[int] = set()
        dealt: Set[int] = set()

        ids = [int(i) for i in post_ids if i is not None]
        if ids:
            negotiating = await EcoViewerContextBuilder._negotiating_post_ids(
                db, viewer_tenant_code, ids
            )
            dealt = await EcoViewerContextBuilder._dealt_post_ids(
                db, viewer_tenant_code, ids
            )

        return EcoViewerContext(
            viewer_tenant_code=viewer_tenant_code,
            license_verified=bool(license_verified),
            is_platform_ops=is_platform_ops,
            negotiating_post_ids=frozenset(negotiating),
            dealt_post_ids=frozenset(dealt),
        )

    @staticmethod
    async def _negotiating_post_ids(
        db: AsyncSession, tenant_code: str, post_ids: List[int]
    ) -> Set[int]:
        """查看方作为发起方、且已进入洽谈及以后的挂牌集合

        只认 TALKING / SELECTED：``PENDING``（待响应）不算洽谈层，此时挂牌方
        还没同意交换联系方式，发起方不能因为「我发起了」就看到对方手机号，
        否则付费用户可以靠批量发起意向来抓取全站联系方式。
        """
        result = await db.execute(
            select(SysEcoIntent.post_id).where(
                SysEcoIntent.initiator_tenant_code == tenant_code,
                SysEcoIntent.post_id.in_(post_ids),
                SysEcoIntent.status.in_(list(IntentStatus.UNLOCKED)),
                SysEcoIntent.is_deleted == 0,
            )
        )
        return {int(x) for x in result.scalars().all()}

    @staticmethod
    async def _dealt_post_ids(
        db: AsyncSession, tenant_code: str, post_ids: List[int]
    ) -> Set[int]:
        """查看方作为合作方、且已确认成交的挂牌集合

        待确认（``PENDING_CONFIRM``）不算成交层，与洽谈层同理。
        """
        active = [s for s in DealStatus.ACTIVE if s != DealStatus.PENDING_CONFIRM]
        result = await db.execute(
            select(SysEcoDeal.post_id).where(
                SysEcoDeal.partner_tenant_code == tenant_code,
                SysEcoDeal.post_id.in_(post_ids),
                SysEcoDeal.status.in_(active + list(DealStatus.TERMINAL)),
                SysEcoDeal.is_deleted == 0,
            )
        )
        return {int(x) for x in result.scalars().all()}

    @staticmethod
    def empty(viewer_tenant_code: str) -> EcoViewerContext:
        """不含任何挂牌关系的上下文（用于「我发布的」等无需层级判定的场景）"""
        return EcoViewerContext(
            viewer_tenant_code=viewer_tenant_code, license_verified=True
        )
