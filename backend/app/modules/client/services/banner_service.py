"""
客户端工作台推广位 Banner 服务

Banner 配置与埋点均存于平台库（zt_platform），Client 通过平台库 Session 读取/写入。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.promotion.banner import (
    PromotionBanner,
    PromotionBannerEvent,
)
from app.modules.console.models.tenant.tenant_product import TenantProduct


class ClientBannerService:
    """客户端 Banner 展示与埋点服务"""

    @staticmethod
    async def _tenant_version_codes(db: AsyncSession, tenant_code: str) -> List[str]:
        """租户当前生效的产品版本编码列表"""
        now_t = datetime.now()
        rows = (
            await db.execute(
                select(TenantProduct.version_code).where(
                    TenantProduct.tenant_code == tenant_code,
                    TenantProduct.is_deleted == 0,
                    TenantProduct.status == 1,
                    or_(
                        TenantProduct.end_time.is_(None),
                        TenantProduct.end_time > now_t,
                    ),
                )
            )
        ).all()
        return [r[0] for r in rows if r[0]]

    @staticmethod
    async def list_visible(db: AsyncSession, tenant_code: str) -> List[dict]:
        """返回当前租户可见的 Banner（已上线 + 在排期内 + 命中定向），按排序返回"""
        now_t = datetime.now()
        query = select(PromotionBanner).where(
            PromotionBanner.is_deleted == 0,
            PromotionBanner.status == "published",
            or_(PromotionBanner.start_at.is_(None), PromotionBanner.start_at <= now_t),
            or_(PromotionBanner.end_at.is_(None), PromotionBanner.end_at >= now_t),
        ).order_by(PromotionBanner.sort_order.asc(), PromotionBanner.id.desc())

        banners = list((await db.execute(query)).scalars().all())

        version_codes: Optional[List[str]] = None
        result: List[dict] = []
        for b in banners:
            if b.target_type == "tenant":
                if not b.target_values or tenant_code not in b.target_values:
                    continue
            elif b.target_type == "version":
                if version_codes is None:
                    version_codes = await ClientBannerService._tenant_version_codes(
                        db, tenant_code
                    )
                if not b.target_values or not (set(b.target_values) & set(version_codes)):
                    continue
            # target_type == "all" 直接命中
            result.append({
                "id": b.id,
                "image_url": b.image_url,
                "title": b.title,
                "link_type": b.link_type,
                "link_url": b.link_url,
                "open_in_new_tab": b.open_in_new_tab,
            })
        return result

    @staticmethod
    async def record_event(
        db: AsyncSession,
        banner_id: int,
        event_type: str,
        tenant_code: str,
        user_id: int,
        user_phone: Optional[str],
        user_agent: Optional[str] = None,
    ) -> bool:
        """记录曝光/点击事件。banner 不存在或已删除则忽略。"""
        banner = (
            await db.execute(
                select(PromotionBanner.id).where(
                    PromotionBanner.id == banner_id,
                    PromotionBanner.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not banner:
            return False

        db.add(PromotionBannerEvent(
            banner_id=banner_id,
            tenant_code=tenant_code,
            user_id=user_id,
            user_phone=user_phone,
            event_type=event_type,
            occurred_at=datetime.now(),
            user_agent=(user_agent or "")[:255] or None,
        ))
        await db.flush()
        return True
