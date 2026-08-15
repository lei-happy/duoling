"""业务主数据只读出口

能源中心其余代码禁止直接 import models/capacity、models/task、models/waybill。
车辆 / 司机 / 运力 / 任务 / 运单查询全部走这里。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class MasterDataResolver:
    """对运营主数据的只读适配"""

    @staticmethod
    async def get_vehicle_by_id(db: AsyncSession, vehicle_id: int) -> Optional[dict]:
        from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle

        r = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == 0)
        )
        v = r.scalar_one_or_none()
        if v is None:
            return None
        return {"id": v.id, "plateNumber": v.plate_number, "status": v.status}

    @staticmethod
    async def get_vehicle_by_plate(db: AsyncSession, plate_number: str) -> Optional[dict]:
        from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle

        plate = (plate_number or "").strip()
        if not plate:
            return None
        r = await db.execute(
            select(Vehicle).where(
                Vehicle.plate_number == plate, Vehicle.is_deleted == 0
            )
        )
        v = r.scalar_one_or_none()
        if v is None:
            return None
        return {"id": v.id, "plateNumber": v.plate_number, "status": v.status}

    @staticmethod
    async def get_driver_by_id(db: AsyncSession, driver_id: int) -> Optional[dict]:
        from app.modules.client.models.capacity.self_capacity.driver.driver import Driver

        r = await db.execute(
            select(Driver).where(Driver.id == driver_id, Driver.is_deleted == 0)
        )
        d = r.scalar_one_or_none()
        if d is None:
            return None
        return {
            "id": d.id,
            "name": getattr(d, "name", None) or getattr(d, "driver_name", None),
            "phone": getattr(d, "phone", None) or getattr(d, "mobile", None),
        }

    @staticmethod
    async def get_capacity_by_vehicle(
        db: AsyncSession, vehicle_id: int
    ) -> Optional[dict]:
        from app.modules.client.models.capacity.self_capacity.capacity import Capacity

        r = await db.execute(
            select(Capacity).where(
                Capacity.vehicle_id == vehicle_id,
                Capacity.status == 1,
                Capacity.is_deleted == 0,
            )
        )
        c = r.scalar_one_or_none()
        if c is None:
            return None
        return {
            "id": c.id,
            "vehicleId": c.vehicle_id,
            "driverId": c.driver_id,
            "driverName": c.driver_name,
            "plateNumber": c.plate_number,
        }

    @staticmethod
    async def find_task_for_vehicle_at(
        db: AsyncSession,
        *,
        vehicle_id: Optional[int],
        plate_number: Optional[str],
        at: datetime,
    ) -> Optional[dict]:
        """消费时间落在任务时间窗口内的任务（车辆匹配）。

        窗口：dispatched_at / actual_load_time / planned_load_time →
        actual_arrive_time / planned_arrive_time（可空表示尚未结束）。
        """
        from app.modules.client.models.capacity.self_capacity.capacity import Capacity
        from app.modules.client.models.task.task import Task

        if at is None:
            return None

        stmt = select(Task).where(Task.is_deleted == 0, Task.status.notin_((7, 9)))
        if vehicle_id:
            cap_ids = (
                await db.execute(
                    select(Capacity.id).where(
                        Capacity.vehicle_id == vehicle_id,
                        Capacity.is_deleted == 0,
                    )
                )
            ).scalars().all()
            if cap_ids:
                stmt = stmt.where(Task.capacity_id.in_(list(cap_ids)))
            elif plate_number:
                stmt = stmt.where(Task.plate_number == plate_number)
            else:
                return None
        elif plate_number:
            stmt = stmt.where(Task.plate_number == plate_number)
        else:
            return None

        rows = (await db.execute(stmt.order_by(Task.id.desc()).limit(20))).scalars().all()
        hits: list[Any] = []
        for t in rows:
            start = t.dispatched_at or t.actual_load_time or t.planned_load_time
            end = t.actual_arrive_time or t.planned_arrive_time
            if start and at < start:
                continue
            if end and at > end:
                continue
            hits.append(t)
        if len(hits) != 1:
            return None
        t = hits[0]
        return {
            "id": t.id,
            "taskNo": t.task_no,
            "plateNumber": t.plate_number,
            "capacityId": t.capacity_id,
        }

    @staticmethod
    async def list_waybill_ids_of_task(db: AsyncSession, task_id: int) -> list[int]:
        from app.modules.client.models.task.task_waybill_item import TaskWaybillItem

        rows = (
            await db.execute(
                select(TaskWaybillItem.waybill_id).where(
                    TaskWaybillItem.task_id == task_id,
                    TaskWaybillItem.is_deleted == 0,
                )
            )
        ).scalars().all()
        return [int(x) for x in rows if x]
