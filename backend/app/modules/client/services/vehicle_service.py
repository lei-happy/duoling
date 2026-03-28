"""
车辆管理服务（租户库）
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.vehicle import Vehicle
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
        base = select(Vehicle).where(Vehicle.is_deleted == 0)

        if keyword:
            base = base.where(
                (Vehicle.plate_number.contains(keyword)) |
                (Vehicle.brand.contains(keyword)) |
                (Vehicle.model.contains(keyword))
            )
        if vehicle_type:
            base = base.where(Vehicle.vehicle_type == vehicle_type)
        if status is not None:
            base = base.where(Vehicle.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Vehicle.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [VehicleOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_vehicle(
        db: AsyncSession, data: VehicleCreate
    ) -> Vehicle:
        existing = await db.execute(
            select(Vehicle).where(
                Vehicle.plate_number == data.plateNumber,
                Vehicle.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"车牌号 {data.plateNumber} 已存在")

        vehicle = Vehicle(
            plate_number=data.plateNumber,
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
        db.add(vehicle)
        await db.flush()
        await db.refresh(vehicle)
        return vehicle

    @staticmethod
    async def update_vehicle(
        db: AsyncSession, vehicle_id: int, data: VehicleUpdate
    ) -> Vehicle:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise BizException("车辆不存在")

        field_map = {
            "plateNumber": "plate_number",
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
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(vehicle, model_field, val)

        await db.flush()
        await db.refresh(vehicle)
        return vehicle

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
        vehicle.is_deleted = 1
        await db.flush()
