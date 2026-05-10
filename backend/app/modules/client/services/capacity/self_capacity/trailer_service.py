"""
挂车管理服务（租户库）
"""

from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.trailer import Trailer
from app.modules.client.models.capacity.self_capacity.trailer_ext import TrailerExt
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.schemas.capacity.self_capacity.trailer import (
    TrailerCreate, TrailerUpdate, TrailerOut, TrailerSimpleOut,
)
from app.modules.client.constants.plate_category import (
    normalize_plate_input,
    validate_trailer_plate_for_category,
)


class TrailerService:

    @staticmethod
    async def page_trailers(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        trailer_type: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = (
            select(
                Trailer,
                TrailerExt,
                Vehicle.plate_number.label("vehicle_plate"),
                Vehicle.plate_category.label("vehicle_pc"),
            )
            .outerjoin(TrailerExt, and_(
                TrailerExt.trailer_id == Trailer.id,
                TrailerExt.is_deleted == 0,
            ))
            .outerjoin(Vehicle, and_(
                Vehicle.trailer_id == Trailer.id,
                Vehicle.is_deleted == 0,
            ))
            .where(Trailer.is_deleted == 0)
        )

        if keyword:
            base = base.where(Trailer.plate_number.contains(keyword))
        if trailer_type:
            base = base.where(TrailerExt.trailer_type == trailer_type)
        if status is not None:
            base = base.where(Trailer.status == status)

        count_q = select(func.count()).select_from(
            select(Trailer.id)
            .outerjoin(TrailerExt, and_(
                TrailerExt.trailer_id == Trailer.id,
                TrailerExt.is_deleted == 0,
            ))
            .where(Trailer.is_deleted == 0)
            .where(Trailer.plate_number.contains(keyword) if keyword else True)
            .where(TrailerExt.trailer_type == trailer_type if trailer_type else True)
            .where(Trailer.status == status if status is not None else True)
            .subquery()
        )
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Trailer.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()

        return {
            "list": [
                TrailerOut.from_row(t, ext, vp, vpc).model_dump()
                for t, ext, vp, vpc in rows
            ],
            "total": total,
            "count": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_trailer(db: AsyncSession, trailer_id: int) -> TrailerOut:
        result = await db.execute(
            select(
                Trailer,
                TrailerExt,
                Vehicle.plate_number.label("vehicle_plate"),
                Vehicle.plate_category.label("vehicle_pc"),
            )
            .outerjoin(TrailerExt, and_(
                TrailerExt.trailer_id == Trailer.id,
                TrailerExt.is_deleted == 0,
            ))
            .outerjoin(Vehicle, and_(
                Vehicle.trailer_id == Trailer.id,
                Vehicle.is_deleted == 0,
            ))
            .where(Trailer.id == trailer_id, Trailer.is_deleted == 0)
        )
        row = result.one_or_none()
        if not row:
            raise BizException("挂车不存在")
        t, ext, vp, vpc = row
        return TrailerOut.from_row(t, ext, vp, vpc)

    @staticmethod
    async def list_available_trailers(
        db: AsyncSession,
        exclude_vehicle_id: Optional[int] = None,
    ) -> list:
        """查询未被其他车辆关联的挂车，用于下拉选择"""
        bound_q = (
            select(Vehicle.trailer_id)
            .where(Vehicle.is_deleted == 0, Vehicle.trailer_id.isnot(None))
        )
        if exclude_vehicle_id:
            bound_q = bound_q.where(Vehicle.id != exclude_vehicle_id)

        result = await db.execute(
            select(Trailer)
            .where(
                Trailer.is_deleted == 0,
                Trailer.status == 1,
                Trailer.id.notin_(bound_q),
            )
            .order_by(Trailer.plate_number)
        )
        trailers = result.scalars().all()
        return [
            TrailerSimpleOut(
                id=t.id,
                plateNumber=t.plate_number,
                plateCategory=t.plate_category,
            ).model_dump()
            for t in trailers
        ]

    @staticmethod
    async def create_trailer(
        db: AsyncSession, data: TrailerCreate
    ) -> TrailerOut:
        plate_norm = normalize_plate_input(data.plateNumber)
        validate_trailer_plate_for_category(data.plateCategory, plate_norm)

        existing = await db.execute(
            select(Trailer).where(
                Trailer.plate_number == plate_norm,
                Trailer.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"挂车车牌号 {plate_norm} 已存在")

        trailer = Trailer(
            plate_number=plate_norm,
            plate_category=data.plateCategory,
            status=1,
        )
        db.add(trailer)
        await db.flush()
        await db.refresh(trailer)

        ext = TrailerExt(
            trailer_id=trailer.id,
            trailer_type=data.trailerType,
            axle_count=data.axleCount,
            load_capacity=data.loadCapacity,
            volume_capacity=data.volumeCapacity,
            length=data.length,
            width=data.width,
            height=data.height,
            parking_spots=data.parkingSpots,
            purchase_date=data.purchaseDate,
            remark=data.remark,
        )
        db.add(ext)
        await db.flush()
        await db.refresh(ext)

        return TrailerOut.from_row(trailer, ext, None, None)

    @staticmethod
    async def update_trailer(
        db: AsyncSession, trailer_id: int, data: TrailerUpdate
    ) -> TrailerOut:
        result = await db.execute(
            select(Trailer).where(
                Trailer.id == trailer_id,
                Trailer.is_deleted == 0,
            )
        )
        trailer = result.scalar_one_or_none()
        if not trailer:
            raise BizException("挂车不存在")

        update_data = data.model_dump(exclude_unset=True)

        if "plateNumber" in update_data and update_data["plateNumber"]:
            new_pn = normalize_plate_input(update_data["plateNumber"])
            if new_pn != trailer.plate_number:
                dup = await db.execute(
                    select(Trailer.id).where(
                        Trailer.plate_number == new_pn,
                        Trailer.is_deleted == 0,
                        Trailer.id != trailer_id,
                    )
                )
                if dup.scalar_one_or_none():
                    raise BizException(f"挂车车牌号 {new_pn} 已存在")
            trailer.plate_number = new_pn

        if "plateCategory" in update_data and update_data["plateCategory"] is not None:
            trailer.plate_category = update_data["plateCategory"]

        if "plateNumber" in update_data or "plateCategory" in update_data:
            validate_trailer_plate_for_category(
                trailer.plate_category, trailer.plate_number
            )

        if "status" in update_data and update_data["status"] is not None:
            trailer.status = update_data["status"]

        ext_fields = {
            "trailerType": "trailer_type",
            "axleCount": "axle_count",
            "loadCapacity": "load_capacity",
            "volumeCapacity": "volume_capacity",
            "length": "length",
            "width": "width",
            "height": "height",
            "parkingSpots": "parking_spots",
            "purchaseDate": "purchase_date",
            "remark": "remark",
        }
        has_ext_update = any(k in update_data for k in ext_fields)
        if has_ext_update:
            ext_result = await db.execute(
                select(TrailerExt).where(
                    TrailerExt.trailer_id == trailer_id,
                    TrailerExt.is_deleted == 0,
                )
            )
            ext = ext_result.scalar_one_or_none()
            if not ext:
                ext = TrailerExt(trailer_id=trailer_id)
                db.add(ext)
                await db.flush()

            for schema_f, model_f in ext_fields.items():
                if schema_f in update_data:
                    setattr(ext, model_f, update_data[schema_f])

        await db.flush()
        return await TrailerService.get_trailer(db, trailer_id)

    @staticmethod
    async def delete_trailer(db: AsyncSession, trailer_id: int) -> None:
        result = await db.execute(
            select(Trailer).where(
                Trailer.id == trailer_id,
                Trailer.is_deleted == 0,
            )
        )
        trailer = result.scalar_one_or_none()
        if not trailer:
            raise BizException("挂车不存在")

        bound = await db.execute(
            select(Vehicle).where(
                Vehicle.trailer_id == trailer_id,
                Vehicle.is_deleted == 0,
            )
        )
        if bound.scalar_one_or_none():
            raise BizException("该挂车已关联车辆，请先解除关联后再删除")

        trailer.is_deleted = 1
        ext_result = await db.execute(
            select(TrailerExt).where(
                TrailerExt.trailer_id == trailer_id,
                TrailerExt.is_deleted == 0,
            )
        )
        ext = ext_result.scalar_one_or_none()
        if ext:
            ext.is_deleted = 1

        await db.flush()
