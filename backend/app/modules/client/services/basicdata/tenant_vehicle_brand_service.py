"""
租户库品牌服务
"""

from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.pagination import paginate
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
        stmt = select(BizVehicleBrand)
        if keyword:
            stmt = stmt.where(BizVehicleBrand.brand_name_cn.contains(keyword.strip()))
        return await paginate(
            db, stmt, page, limit,
            order_by=BizVehicleBrand.brand_id,
            serializer=lambda r: VehicleBrandOut.from_model(r).model_dump(),
        )

    @staticmethod
    def _brand_options_base_stmt(keyword: Optional[str] = None):
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
        )
        if keyword:
            kw = keyword.strip()
            if kw:
                stmt = stmt.where(BizVehicleBrand.brand_name_cn.contains(kw))
        return stmt

    @staticmethod
    def _serialize_brand_option(brand: BizVehicleBrand, series_count) -> dict:
        return {
            "brandId": brand.brand_id,
            "brandNameCn": brand.brand_name_cn,
            "brandLogo": brand.brand_logo,
            "seriesCount": int(series_count or 0),
        }

    @staticmethod
    async def list_brand_options(
        db: AsyncSession,
        keyword: Optional[str] = None,
        limit: int = 2000,
    ) -> list:
        stmt = (
            TenantVehicleBrandService._brand_options_base_stmt(keyword)
            .order_by(BizVehicleBrand.brand_name_cn)
            .limit(min(limit, 5000))
        )
        result = await db.execute(stmt)
        return [
            TenantVehicleBrandService._serialize_brand_option(brand, series_count)
            for brand, series_count in result.all()
        ]

    @staticmethod
    async def page_brand_options(
        db: AsyncSession,
        page: int = 1,
        limit: int = 50,
        keyword: Optional[str] = None,
    ) -> dict:
        """分页品牌选项（含车系数量），供侧栏滚动加载。"""
        count_stmt = select(func.count()).select_from(BizVehicleBrand)
        if keyword:
            kw = keyword.strip()
            if kw:
                count_stmt = count_stmt.where(
                    BizVehicleBrand.brand_name_cn.contains(kw)
                )
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            TenantVehicleBrandService._brand_options_base_stmt(keyword)
            .order_by(BizVehicleBrand.brand_name_cn)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = [
            TenantVehicleBrandService._serialize_brand_option(brand, series_count)
            for brand, series_count in result.all()
        ]
        return {"list": items, "count": total}

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
