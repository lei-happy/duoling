"""
地名 / 车型 别名维护服务（Phase 4 - 异常中心配套）
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.region_alias import RegionAlias
from app.modules.client.models.billing.vehicle_alias import VehicleAlias
from app.modules.client.services.billing.standardize_service import vehicle_alias_key


# ============== 地名别名 ==============

class RegionAliasService:

    @staticmethod
    async def page(
        db: AsyncSession, page: int = 1, page_size: int = 20,
        keyword: Optional[str] = None,
    ) -> dict:
        base = select(RegionAlias).where(RegionAlias.is_deleted == 0)
        if keyword:
            base = base.where(RegionAlias.alias_name.contains(keyword))
        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        r = await db.execute(
            base.order_by(RegionAlias.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = []
        for a in r.scalars().all():
            items.append({
                "id": a.id, "aliasName": a.alias_name,
                "regionId": a.region_id, "status": a.status,
                "createdAt": a.created_at,
            })
        return {"list": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def upsert(
        db: AsyncSession, alias_name: str, region_id: int
    ) -> RegionAlias:
        s = (alias_name or "").strip()
        if not s:
            raise BizException("别名不能为空")
        if not region_id:
            raise BizException("region_id 必填")
        r = await db.execute(
            select(RegionAlias).where(RegionAlias.alias_name == s)
        )
        existed = r.scalar_one_or_none()
        if existed:
            existed.region_id = region_id
            existed.status = 1
            existed.is_deleted = 0
            await db.flush()
            await db.refresh(existed)
            return existed
        m = RegionAlias(alias_name=s, region_id=region_id, status=1)
        db.add(m)
        await db.flush()
        await db.refresh(m)
        return m

    @staticmethod
    async def delete(db: AsyncSession, alias_id: int) -> None:
        r = await db.execute(
            select(RegionAlias).where(
                RegionAlias.id == alias_id, RegionAlias.is_deleted == 0,
            )
        )
        m = r.scalar_one_or_none()
        if not m:
            raise BizException("别名不存在")
        m.is_deleted = 1
        await db.flush()


# ============== 车型 / 品牌别名 ==============

class VehicleAliasService:

    @staticmethod
    async def page(
        db: AsyncSession, page: int = 1, page_size: int = 20,
        keyword: Optional[str] = None, kind: Optional[str] = None,
    ) -> dict:
        base = select(VehicleAlias).where(VehicleAlias.is_deleted == 0)
        if keyword:
            base = base.where(VehicleAlias.alias_name.contains(keyword))
        if kind:
            base = base.where(VehicleAlias.alias_kind == kind)
        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        r = await db.execute(
            base.order_by(VehicleAlias.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = []
        for a in r.scalars().all():
            items.append({
                "id": a.id,
                "aliasName": a.alias_name,
                "aliasKind": a.alias_kind,
                "brandId": a.brand_id,
                "seriesId": a.series_id,
                "status": a.status,
                "createdAt": a.created_at,
            })
        return {"list": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def upsert(
        db: AsyncSession,
        *,
        alias_kind: str,
        raw_brand: Optional[str],
        raw_model: Optional[str],
        brand_id: Optional[int],
        series_id: Optional[int],
    ) -> VehicleAlias:
        if alias_kind not in ("brand", "series"):
            raise BizException("alias_kind 只能为 brand/series")
        if alias_kind == "brand":
            alias_name = (raw_brand or "").strip()
            if not (alias_name and brand_id):
                raise BizException("品牌别名需要 raw_brand + brand_id")
        else:
            alias_name = vehicle_alias_key(raw_brand, raw_model)
            if not (raw_brand or raw_model) or not (brand_id and series_id):
                raise BizException("车系别名需要 raw_brand/raw_model + brand_id + series_id")

        r = await db.execute(
            select(VehicleAlias).where(VehicleAlias.alias_name == alias_name)
        )
        existed = r.scalar_one_or_none()
        if existed:
            existed.alias_kind = alias_kind
            existed.brand_id = brand_id
            existed.series_id = series_id
            existed.status = 1
            existed.is_deleted = 0
            await db.flush()
            await db.refresh(existed)
            return existed
        m = VehicleAlias(
            alias_name=alias_name, alias_kind=alias_kind,
            brand_id=brand_id, series_id=series_id, status=1,
        )
        db.add(m)
        await db.flush()
        await db.refresh(m)
        return m

    @staticmethod
    async def delete(db: AsyncSession, alias_id: int) -> None:
        r = await db.execute(
            select(VehicleAlias).where(
                VehicleAlias.id == alias_id, VehicleAlias.is_deleted == 0,
            )
        )
        m = r.scalar_one_or_none()
        if not m:
            raise BizException("别名不存在")
        m.is_deleted = 1
        await db.flush()
