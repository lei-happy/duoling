"""
车辆管理服务（租户库）

核心表 + 扩展表双表联查、联写逻辑。
"""

from typing import Optional

from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.capacity.self_capacity.trailer import Trailer
from app.modules.client.schemas.capacity.self_capacity.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleOut,
)
from app.modules.client.constants.plate_category import (
    normalize_plate_input,
    validate_plate_for_category,
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
            select(
                Vehicle,
                VehicleExt,
                Trailer.plate_number.label("trailer_plate"),
                Trailer.plate_category.label("trailer_cat"),
            )
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
                or_(
                    Vehicle.plate_number.contains(keyword),
                    VehicleExt.brand.contains(keyword),
                    VehicleExt.model.contains(keyword),
                    Trailer.plate_number.contains(keyword),
                )
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
            .outerjoin(Trailer, and_(
                Trailer.id == Vehicle.trailer_id,
                Trailer.is_deleted == 0,
            ))
            .where(Vehicle.is_deleted == 0)
            .where(
                or_(
                    Vehicle.plate_number.contains(keyword),
                    VehicleExt.brand.contains(keyword),
                    VehicleExt.model.contains(keyword),
                    Trailer.plate_number.contains(keyword),
                ) if keyword else True
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
                VehicleOut.from_row(v, ext, tp, tc).model_dump()
                for v, ext, tp, tc in rows
            ],
            "total": total,
            "count": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_vehicle(db: AsyncSession, vehicle_id: int) -> VehicleOut:
        result = await db.execute(
            select(
                Vehicle,
                VehicleExt,
                Trailer.plate_number.label("trailer_plate"),
                Trailer.plate_category.label("trailer_cat"),
            )
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
        v, ext, tp, tc = row
        return VehicleOut.from_row(v, ext, tp, tc)

    @staticmethod
    async def create_vehicle(
        db: AsyncSession, data: VehicleCreate
    ) -> VehicleOut:
        plate_norm = normalize_plate_input(data.plateNumber)
        validate_plate_for_category(data.plateCategory, plate_norm)

        existing = await db.execute(
            select(Vehicle).where(
                Vehicle.plate_number == plate_norm,
                Vehicle.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"车牌号 {plate_norm} 已存在")

        if data.trailerId:
            await VehicleService._check_trailer_bindable(db, data.trailerId)

        vehicle = Vehicle(
            plate_number=plate_norm,
            plate_category=data.plateCategory,
            trailer_id=data.trailerId,
            status=1,
            status_source="manual",
        )
        db.add(vehicle)
        await db.flush()
        await db.refresh(vehicle)

        # 清除同 vehicle_id 的残留扩展行（孤儿数据或仅软删导致 UNIQUE 冲突）
        await db.execute(
            delete(VehicleExt).where(VehicleExt.vehicle_id == vehicle.id)
        )
        await db.flush()

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
        trailer_plate_category = None
        if vehicle.trailer_id:
            r = await db.execute(
                select(Trailer.plate_number, Trailer.plate_category).where(
                    Trailer.id == vehicle.trailer_id
                )
            )
            trow = r.one_or_none()
            if trow:
                trailer_plate, trailer_plate_category = trow[0], trow[1]

        return VehicleOut.from_row(vehicle, ext, trailer_plate, trailer_plate_category)

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

        if "trailerId" in update_data:
            tid = update_data["trailerId"]
            if tid is not None:
                await VehicleService._check_trailer_bindable(
                    db, tid, exclude_vehicle_id=vehicle_id
                )
            vehicle.trailer_id = tid

        if "status" in update_data and update_data["status"] is not None:
            vehicle.status = update_data["status"]

        if "plateNumber" in update_data and update_data["plateNumber"]:
            new_pn = normalize_plate_input(update_data["plateNumber"])
            if new_pn != vehicle.plate_number:
                dup = await db.execute(
                    select(Vehicle.id).where(
                        Vehicle.plate_number == new_pn,
                        Vehicle.is_deleted == 0,
                        Vehicle.id != vehicle_id,
                    )
                )
                if dup.scalar_one_or_none():
                    raise BizException(f"车牌号 {new_pn} 已存在")
            vehicle.plate_number = new_pn

        if "plateCategory" in update_data and update_data["plateCategory"] is not None:
            vehicle.plate_category = update_data["plateCategory"]

        if "plateNumber" in update_data or "plateCategory" in update_data:
            validate_plate_for_category(
                vehicle.plate_category, vehicle.plate_number
            )

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
                select(VehicleExt).where(VehicleExt.vehicle_id == vehicle_id)
            )
            ext = ext_result.scalar_one_or_none()
            if not ext:
                ext = VehicleExt(vehicle_id=vehicle_id)
                db.add(ext)
                await db.flush()
            elif ext.is_deleted:
                ext.is_deleted = 0

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
