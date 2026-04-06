"""
Console 平台车系服务
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.basicdata.basicdata_brand import BasicdataBrand
from app.modules.console.models.basicdata.basicdata_car_series import BasicdataCarSeries
from app.modules.console.schemas.basicdata.vehicle_series import (
    VehicleSeriesCreate,
    VehicleSeriesUpdate,
    VehicleSeriesOut,
)


class VehicleSeriesService:

    @staticmethod
    async def page_series(
        db: AsyncSession,
        brand_id: int,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
    ) -> dict:
        exists = await db.execute(
            select(BasicdataBrand.brand_id).where(
                BasicdataBrand.brand_id == brand_id
            )
        )
        if exists.scalar_one_or_none() is None:
            raise BizException("品牌不存在")

        base = select(BasicdataCarSeries).where(
            BasicdataCarSeries.brand_id == brand_id
        )
        if keyword:
            base = base.where(BasicdataCarSeries.series_name.contains(keyword.strip()))

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(BasicdataCarSeries.series_id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()
        items = [VehicleSeriesOut.from_model(r).model_dump() for r in rows]
        return {"list": items, "count": count}

    @staticmethod
    async def get_series(db: AsyncSession, series_id: int) -> VehicleSeriesOut:
        result = await db.execute(
            select(BasicdataCarSeries).where(
                BasicdataCarSeries.series_id == series_id
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("车系不存在")
        return VehicleSeriesOut.from_model(row)

    @staticmethod
    def _to_decimal(v) -> Optional[Decimal]:
        if v is None:
            return None
        return Decimal(str(v))

    @staticmethod
    async def create_series(
        db: AsyncSession, data: VehicleSeriesCreate
    ) -> BasicdataCarSeries:
        exists = await db.execute(
            select(BasicdataBrand.brand_id).where(
                BasicdataBrand.brand_id == data.brandId
            )
        )
        if exists.scalar_one_or_none() is None:
            raise BizException("品牌不存在")
        row = BasicdataCarSeries(
            brand_id=data.brandId,
            price=data.price,
            series_image=data.seriesImage,
            series_name=data.seriesName,
            energy_type=data.energyType,
            length_mm=data.lengthMm,
            width_mm=data.widthMm,
            height_mm=data.heightMm,
            wheelbase_mm=data.wheelbaseMm,
            front_track_mm=data.frontTrackMm,
            rear_track_mm=data.rearTrackMm,
            approach_angle=VehicleSeriesService._to_decimal(data.approachAngle),
            departure_angle=VehicleSeriesService._to_decimal(data.departureAngle),
            curb_weight_kg=data.curbWeightKg,
        )
        db.add(row)
        await db.flush()
        return row

    @staticmethod
    async def update_series(
        db: AsyncSession, series_id: int, data: VehicleSeriesUpdate
    ) -> BasicdataCarSeries:
        result = await db.execute(
            select(BasicdataCarSeries).where(
                BasicdataCarSeries.series_id == series_id
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("车系不存在")
        if data.price is not None:
            row.price = data.price
        if data.seriesImage is not None:
            row.series_image = data.seriesImage
        if data.seriesName is not None:
            row.series_name = data.seriesName
        if data.energyType is not None:
            row.energy_type = data.energyType
        if data.lengthMm is not None:
            row.length_mm = data.lengthMm
        if data.widthMm is not None:
            row.width_mm = data.widthMm
        if data.heightMm is not None:
            row.height_mm = data.heightMm
        if data.wheelbaseMm is not None:
            row.wheelbase_mm = data.wheelbaseMm
        if data.frontTrackMm is not None:
            row.front_track_mm = data.frontTrackMm
        if data.rearTrackMm is not None:
            row.rear_track_mm = data.rearTrackMm
        if data.approachAngle is not None:
            row.approach_angle = VehicleSeriesService._to_decimal(
                data.approachAngle
            )
        if data.departureAngle is not None:
            row.departure_angle = VehicleSeriesService._to_decimal(
                data.departureAngle
            )
        if data.curbWeightKg is not None:
            row.curb_weight_kg = data.curbWeightKg
        await db.flush()
        return row

    @staticmethod
    async def delete_series(db: AsyncSession, series_id: int) -> None:
        result = await db.execute(
            select(BasicdataCarSeries).where(
                BasicdataCarSeries.series_id == series_id
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("车系不存在")
        await db.execute(
            delete(BasicdataCarSeries).where(
                BasicdataCarSeries.series_id == series_id
            )
        )
