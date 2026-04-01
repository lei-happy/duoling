"""
车辆管理服务（租户库）

核心表 + 扩展表双表联查、联写逻辑。
"""

from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.vehicle import Vehicle
from app.modules.client.models.vehicle_ext import VehicleExt
from app.modules.client.models.trailer import Trailer
from app.modules.client.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleOut,
)


class VehicleService:

    @staticmethod
    async def page_vehicles(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = (
            select(Vehicle, VehicleExt, Trailer.plate_number.label("trailer_plate"))
            .outerjoin(VehicleExt, and_(
                VehicleExt.vehicle_id == Vehicle.id,
                VehicleExt.is_deleted == 0,
            ))
            .outerjoin(Trailer, and_(
                Trailer.id == Vehicle.trailer_id,
                Trailer.is_deleted == 0,
            ))
            .where(Vehicle.is_deleted == 0)
        )

        if keyword:
            base = base.where(
                (Vehicle.plate_number.contains(keyword)) |
                (VehicleExt.brand.contains(keyword)) |
                (VehicleExt.model.contains(keyword))
            )
        if vehicle_type:
            base = base.where(VehicleExt.vehicle_type == vehicle_type)
        if status is not None:
            base = base.where(Vehicle.status == status)

        count_q = select(func.count()).select_from(
            select(Vehicle.id)
            .outerjoin(VehicleExt, and_(
                VehicleExt.vehicle_id == Vehicle.id,
                VehicleExt.is_deleted == 0,
            ))
            .where(Vehicle.is_deleted == 0)
            .where(
                (Vehicle.plate_number.contains(keyword) |
                 VehicleExt.brand.contains(keyword) |
                 VehicleExt.model.contains(keyword)) if keyword else True
            )
            .where(VehicleExt.vehicle_type == vehicle_type if vehicle_type else True)
            .where(Vehicle.status == status if status is not None else True)
            .subquery()
        )
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Vehicle.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()

        return {
            "list": [
                VehicleOut.from_row(v, ext, tp).model_dump()
                for v, ext, tp in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_vehicle(db: AsyncSession, vehicle_id: int) -> VehicleOut:
        result = await db.execute(
            select(Vehicle, VehicleExt, Trailer.plate_number.label("trailer_plate"))
            .outerjoin(VehicleExt, and_(
                VehicleExt.vehicle_id == Vehicle.id,
                VehicleExt.is_deleted == 0,
            ))
            .outerjoin(Trailer, and_(
                Trailer.id == Vehicle.trailer_id,
                Trailer.is_deleted == 0,
            ))
            .where(Vehicle.id == vehicle_id, Vehicle.is_deleted == 0)
        )
        row = result.one_or_none()
        if not row:
            raise BizException("车辆不存在")
        v, ext, tp = row
        return VehicleOut.from_row(v, ext, tp)

    @staticmethod
    async def create_vehicle(
        db: AsyncSession, data: VehicleCreate
    ) -> VehicleOut:
        existing = await db.execute(
            select(Vehicle).where(
                Vehicle.plate_number == data.plateNumber,
                Vehicle.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"车牌号 {data.plateNumber} 已存在")

        if data.trailerId:
            await VehicleService._check_trailer_bindable(db, data.trailerId)

        vehicle = Vehicle(
            plate_number=data.plateNumber,
            trailer_id=data.trailerId,
            status=1,
            status_source="manual",
        )
        db.add(vehicle)
        await db.flush()
        await db.refresh(vehicle)

        ext = VehicleExt(
            vehicle_id=vehicle.id,
            vehicle_type=data.vehicleType,
            brand=data.brand,
            model=data.model,
            color=data.color,
            vin=data.vin,
            engine_no=data.engineNo,
            load_capacity=data.loadCapacity,
            volume_capacity=data.volumeCapacity,
            purchase_date=data.purchaseDate,
            insurance_expire=data.insuranceExpire,
            inspection_expire=data.inspectionExpire,
            gps_device_id=data.gpsDeviceId,
            remark=data.remark,
        )
        db.add(ext)
        await db.flush()
        await db.refresh(ext)

        trailer_plate = None
        if vehicle.trailer_id:
            r = await db.execute(
                select(Trailer.plate_number).where(Trailer.id == vehicle.trailer_id)
            )
            trailer_plate = r.scalar_one_or_none()

        return VehicleOut.from_row(vehicle, ext, trailer_plate)

    @staticmethod
    async def update_vehicle(
        db: AsyncSession, vehicle_id: int, data: VehicleUpdate
    ) -> VehicleOut:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise BizException("车辆不存在")

        update_data = data.model_dump(exclude_unset=True)

        core_fields = {
            "plateNumber": "plate_number",
            "trailerId": "trailer_id",
            "status": "status",
        }
        for schema_f, model_f in core_fields.items():
            if schema_f in update_data:
                if schema_f == "trailerId" and update_data[schema_f] is not None:
                    await VehicleService._check_trailer_bindable(
                        db, update_data[schema_f], exclude_vehicle_id=vehicle_id
                    )
                setattr(vehicle, model_f, update_data[schema_f])

        ext_fields = {
            "vehicleType": "vehicle_type",
            "brand": "brand",
            "model": "model",
            "color": "color",
            "vin": "vin",
            "engineNo": "engine_no",
            "loadCapacity": "load_capacity",
            "volumeCapacity": "volume_capacity",
            "purchaseDate": "purchase_date",
            "insuranceExpire": "insurance_expire",
            "inspectionExpire": "inspection_expire",
            "gpsDeviceId": "gps_device_id",
            "remark": "remark",
        }
        has_ext_update = any(k in update_data for k in ext_fields)
        if has_ext_update:
            ext_result = await db.execute(
                select(VehicleExt).where(
                    VehicleExt.vehicle_id == vehicle_id,
                    VehicleExt.is_deleted == 0,
                )
            )
            ext = ext_result.scalar_one_or_none()
            if not ext:
                ext = VehicleExt(vehicle_id=vehicle_id)
                db.add(ext)
                await db.flush()

            for schema_f, model_f in ext_fields.items():
                if schema_f in update_data:
                    setattr(ext, model_f, update_data[schema_f])

        await db.flush()
        return await VehicleService.get_vehicle(db, vehicle_id)

    @staticmethod
    async def delete_vehicle(db: AsyncSession, vehicle_id: int) -> None:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise BizException("车辆不存在")

        vehicle.trailer_id = None
        vehicle.is_deleted = 1

        ext_result = await db.execute(
            select(VehicleExt).where(
                VehicleExt.vehicle_id == vehicle_id,
                VehicleExt.is_deleted == 0,
            )
        )
        ext = ext_result.scalar_one_or_none()
        if ext:
            ext.is_deleted = 1

        await db.flush()

    @staticmethod
    async def _check_trailer_bindable(
        db: AsyncSession, trailer_id: int, exclude_vehicle_id: int = None
    ) -> None:
        """校验挂车是否可被关联"""
        trailer_r = await db.execute(
            select(Trailer).where(
                Trailer.id == trailer_id,
                Trailer.is_deleted == 0,
            )
        )
        if not trailer_r.scalar_one_or_none():
            raise BizException("挂车不存在")

        q = select(Vehicle).where(
            Vehicle.trailer_id == trailer_id,
            Vehicle.is_deleted == 0,
        )
        if exclude_vehicle_id:
            q = q.where(Vehicle.id != exclude_vehicle_id)
        bound = await db.execute(q)
        if bound.scalar_one_or_none():
            raise BizException("该挂车已被其他车辆关联")
