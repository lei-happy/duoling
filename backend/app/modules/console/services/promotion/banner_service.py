"""
推广位 Banner 管理服务（Console）
"""

from typing import Optional, Tuple, List

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.promotion.banner import (
    PromotionBanner,
    PromotionBannerEvent,
)
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.schemas.promotion.banner import (
    BannerCreate,
    BannerUpdate,
    STATUSES,
)


class BannerService:
    """推广位 Banner 管理服务"""

    # ---- CRUD ----

    @staticmethod
    async def page(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> Tuple[List[PromotionBanner], int]:
        query = select(PromotionBanner).where(PromotionBanner.is_deleted == 0)
        if keyword:
            query = query.where(PromotionBanner.title.like(f"%{keyword}%"))
        if status:
            query = query.where(PromotionBanner.status == status)
        if target_type:
            query = query.where(PromotionBanner.target_type == target_type)

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        query = query.order_by(
            PromotionBanner.sort_order.asc(), PromotionBanner.id.desc()
        ).offset((page - 1) * limit).limit(limit)
        items = list((await db.execute(query)).scalars().all())
        return items, total

    @staticmethod
    async def get_by_id(db: AsyncSession, banner_id: int) -> Optional[PromotionBanner]:
        result = await db.execute(
            select(PromotionBanner).where(
                PromotionBanner.id == banner_id, PromotionBanner.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, data: BannerCreate, created_by: Optional[int]
    ) -> PromotionBanner:
        banner = PromotionBanner(**data.model_dump(), status="draft", created_by=created_by)
        db.add(banner)
        await db.flush()
        # server_default 生成的 created_at/updated_at 在 flush 后处于过期态，
        # 需在异步上下文内 refresh 加载，避免同步序列化时触发 MissingGreenlet
        await db.refresh(banner)
        return banner

    @staticmethod
    async def update(
        db: AsyncSession, banner_id: int, data: BannerUpdate
    ) -> PromotionBanner:
        banner = await BannerService.get_by_id(db, banner_id)
        if not banner:
            raise BizException("Banner 不存在")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(banner, key, value)
        await db.flush()
        await db.refresh(banner)
        return banner

    @staticmethod
    async def delete(db: AsyncSession, banner_id: int) -> None:
        banner = await BannerService.get_by_id(db, banner_id)
        if not banner:
            raise BizException("Banner 不存在")
        banner.is_deleted = 1
        await db.flush()

    @staticmethod
    async def change_status(db: AsyncSession, banner_id: int, status: str) -> PromotionBanner:
        if status not in STATUSES:
            raise BizException("非法状态")
        banner = await BannerService.get_by_id(db, banner_id)
        if not banner:
            raise BizException("Banner 不存在")
        if status == "published":
            if not banner.image_url:
                raise BizException("请先配置 Banner 图片再上线")
        banner.status = status
        await db.flush()
        return banner

    # ---- 定向下拉 ----

    @staticmethod
    async def version_options(db: AsyncSession) -> List[dict]:
        rows = (
            await db.execute(
                select(ProductVersion.version_code, ProductVersion.version_name).where(
                    ProductVersion.is_deleted == 0
                ).order_by(ProductVersion.sort_order.asc())
            )
        ).all()
        return [{"value": r[0], "label": r[1]} for r in rows]

    @staticmethod
    async def tenant_options(
        db: AsyncSession, keyword: Optional[str] = None, limit: int = 50
    ) -> List[dict]:
        query = select(Tenant.tenant_code, Tenant.tenant_name).where(Tenant.is_deleted == 0)
        if keyword:
            query = query.where(Tenant.tenant_name.like(f"%{keyword}%"))
        query = query.order_by(Tenant.id.desc()).limit(limit)
        rows = (await db.execute(query)).all()
        return [{"value": r[0], "label": r[1]} for r in rows]

    # ---- 统计 ----

    @staticmethod
    async def _tenant_name_map(db: AsyncSession, codes: List[str]) -> dict:
        if not codes:
            return {}
        rows = (
            await db.execute(
                select(Tenant.tenant_code, Tenant.tenant_name).where(
                    Tenant.tenant_code.in_(codes)
                )
            )
        ).all()
        return {r[0]: r[1] for r in rows}

    @staticmethod
    async def stats_summary(db: AsyncSession, banner_id: int) -> dict:
        """曝光/点击的 PV/UV + CTR"""
        E = PromotionBannerEvent
        rows = (
            await db.execute(
                select(
                    E.event_type,
                    func.count().label("pv"),
                    func.count(distinct(E.user_id)).label("uv"),
                ).where(E.banner_id == banner_id).group_by(E.event_type)
            )
        ).all()
        agg = {r[0]: {"pv": r[1], "uv": r[2]} for r in rows}
        view = agg.get("view", {"pv": 0, "uv": 0})
        click = agg.get("click", {"pv": 0, "uv": 0})
        ctr = round(click["uv"] / view["uv"], 4) if view["uv"] else 0.0
        return {
            "view_pv": view["pv"],
            "view_uv": view["uv"],
            "click_pv": click["pv"],
            "click_uv": click["uv"],
            "ctr": ctr,
        }

    @staticmethod
    async def stats_by_tenant(db: AsyncSession, banner_id: int) -> List[dict]:
        """按租户聚合曝光/点击"""
        E = PromotionBannerEvent
        rows = (
            await db.execute(
                select(
                    E.tenant_code,
                    E.event_type,
                    func.count().label("pv"),
                    func.count(distinct(E.user_id)).label("uv"),
                ).where(E.banner_id == banner_id).group_by(E.tenant_code, E.event_type)
            )
        ).all()
        acc: dict = {}
        for tenant_code, event_type, pv, uv in rows:
            item = acc.setdefault(
                tenant_code,
                {"tenant_code": tenant_code, "view_pv": 0, "view_uv": 0,
                 "click_pv": 0, "click_uv": 0},
            )
            item[f"{event_type}_pv"] = pv
            item[f"{event_type}_uv"] = uv

        name_map = await BannerService._tenant_name_map(db, list(acc.keys()))
        result = []
        for code, item in acc.items():
            item["tenant_name"] = name_map.get(code)
            result.append(item)
        result.sort(key=lambda x: (x["click_uv"], x["view_uv"]), reverse=True)
        return result

    @staticmethod
    async def event_page(
        db: AsyncSession,
        banner_id: int,
        page: int = 1,
        limit: int = 20,
        event_type: Optional[str] = None,
        tenant_code: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        E = PromotionBannerEvent
        query = select(E).where(E.banner_id == banner_id)
        if event_type:
            query = query.where(E.event_type == event_type)
        if tenant_code:
            query = query.where(E.tenant_code == tenant_code)

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        query = query.order_by(E.occurred_at.desc()).offset((page - 1) * limit).limit(limit)
        events = list((await db.execute(query)).scalars().all())

        name_map = await BannerService._tenant_name_map(
            db, list({e.tenant_code for e in events})
        )
        items = [
            {
                "id": e.id,
                "tenant_code": e.tenant_code,
                "tenant_name": name_map.get(e.tenant_code),
                "user_id": e.user_id,
                "user_phone": e.user_phone,
                "event_type": e.event_type,
                "occurred_at": e.occurred_at,
            }
            for e in events
        ]
        return items, total
