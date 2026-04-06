"""
租户库品牌服务
"""

from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import BizVehicleBrand
from app.modules.client.models.vehicle_basic.biz_vehicle_series import BizVehicleSeries
from app.modules.client.schemas.basicdata.vehicle_brand import (
    VehicleBrandCreate,
    VehicleBrandUpdate,
    VehicleBrandOut,
)


class TenantVehicleBrandService:

    @staticmethod
    async def page_brands(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
    ) -> dict:
        base = select(BizVehicleBrand)
        if keyword:
            base = base.where(BizVehicleBrand.brand_name_cn.contains(keyword.strip()))

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(BizVehicleBrand.brand_id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()
        items = [VehicleBrandOut.from_model(r).model_dump() for r in rows]
        return {"list": items, "count": count}

    @staticmethod
    async def list_brand_options(
        db: AsyncSession,
        keyword: Optional[str] = None,
        limit: int = 2000,
    ) -> list:
        series_cnt = (
            select(
                BizVehicleSeries.brand_id.label("bid"),
                func.count().label("series_cnt"),
            )
            .group_by(BizVehicleSeries.brand_id)
            .subquery()
        )
        stmt = (
            select(
                BizVehicleBrand,
                func.coalesce(series_cnt.c.series_cnt, 0).label("series_count"),
            )
            .outerjoin(series_cnt, BizVehicleBrand.brand_id == series_cnt.c.bid)
            .order_by(BizVehicleBrand.brand_name_cn)
        )
        if keyword:
            kw = keyword.strip()
            if kw:
                stmt = stmt.where(BizVehicleBrand.brand_name_cn.contains(kw))
        stmt = stmt.limit(min(limit, 5000))
        result = await db.execute(stmt)
        return [
            {
                "brandId": brand.brand_id,
                "brandNameCn": brand.brand_name_cn,
                "brandLogo": brand.brand_logo,
                "seriesCount": int(series_count or 0),
            }
            for brand, series_count in result.all()
        ]

    @staticmethod
    async def get_brand(db: AsyncSession, brand_id: int) -> VehicleBrandOut:
        result = await db.execute(
            select(BizVehicleBrand).where(BizVehicleBrand.brand_id == brand_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("品牌不存在")
        return VehicleBrandOut.from_model(row)

    @staticmethod
    async def create_brand(
        db: AsyncSession, data: VehicleBrandCreate
    ) -> BizVehicleBrand:
        row = BizVehicleBrand(
            brand_logo=data.brandLogo,
            brand_name_cn=data.brandNameCn,
            brand_country=data.brandCountry,
            brand_introduce=data.brandIntroduce,
        )
        db.add(row)
        await db.flush()
        return row

    @staticmethod
    async def update_brand(
        db: AsyncSession, brand_id: int, data: VehicleBrandUpdate
    ) -> BizVehicleBrand:
        result = await db.execute(
            select(BizVehicleBrand).where(BizVehicleBrand.brand_id == brand_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("品牌不存在")
        if data.brandLogo is not None:
            row.brand_logo = data.brandLogo
        if data.brandNameCn is not None:
            row.brand_name_cn = data.brandNameCn
        if data.brandCountry is not None:
            row.brand_country = data.brandCountry
        if data.brandIntroduce is not None:
            row.brand_introduce = data.brandIntroduce
        await db.flush()
        return row

    @staticmethod
    async def delete_brand(db: AsyncSession, brand_id: int) -> None:
        cnt_result = await db.execute(
            select(func.count()).select_from(BizVehicleSeries).where(
                BizVehicleSeries.brand_id == brand_id
            )
        )
        if (cnt_result.scalar() or 0) > 0:
            raise BizException("该品牌下仍有车系，无法删除")
        result = await db.execute(
            select(BizVehicleBrand).where(BizVehicleBrand.brand_id == brand_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("品牌不存在")
        await db.execute(
            delete(BizVehicleBrand).where(BizVehicleBrand.brand_id == brand_id)
        )
