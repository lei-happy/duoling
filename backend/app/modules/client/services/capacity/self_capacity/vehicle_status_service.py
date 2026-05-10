"""
车辆状态变更服务（预留扩展）

提供统一的状态变更入口，后续维修保养、车险管理等模块
可通过调用此服务驱动车辆状态流转。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle


class VehicleStatusService:

    VALID_STATUSES = {0, 1, 2, 3, 9}

    @staticmethod
    async def change_status(
        db: AsyncSession,
        vehicle_id: int,
        new_status: int,
        source: str = "manual",
    ) -> Vehicle:
        if new_status not in VehicleStatusService.VALID_STATUSES:
            raise BizException(f"无效的状态值: {new_status}")

        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise BizException("车辆不存在")

        vehicle.status = new_status
        vehicle.status_source = source
        await db.flush()
        return vehicle
