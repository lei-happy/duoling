"""能源中心对外只读门面

finance / billing / insight 读取能源成本时只走本适配器。
一期无调用方，签名保持稳定。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.consumption import EnergyConsumption
from app.modules.client.models.energy.cost_allocation import EnergyCostAllocation
from app.modules.client.services.energy.constants import (
    DIM_DRIVER,
    DIM_TASK,
    DIM_VEHICLE,
    DIM_WAYBILL,
)


def _as_dt_start(d: date | datetime) -> datetime:
    if isinstance(d, datetime):
        return d
    return datetime(d.year, d.month, d.day)


def _as_dt_end(d: date | datetime) -> datetime:
    if isinstance(d, datetime):
        return d
    return datetime(d.year, d.month, d.day, 23, 59, 59)


class EnergyQueryAdapter:
    """只读：按车辆 / 司机 / 任务 / 运单汇总能源成本。"""

    @staticmethod
    async def get_vehicle_energy_cost(
        db: AsyncSession,
        vehicle_ids: Sequence[int],
        start: date | datetime,
        end: date | datetime,
    ) -> dict[int, Decimal]:
        return await _sum_from_allocation_or_flow(
            db, DIM_VEHICLE, "vehicle_id", vehicle_ids, start, end,
        )

    @staticmethod
    async def get_driver_energy_cost(
        db: AsyncSession,
        driver_ids: Sequence[int],
        start: date | datetime,
        end: date | datetime,
    ) -> dict[int, Decimal]:
        return await _sum_from_allocation_or_flow(
            db, DIM_DRIVER, "driver_id", driver_ids, start, end,
        )

    @staticmethod
    async def get_task_energy_cost(
        db: AsyncSession,
        task_ids: Sequence[int],
    ) -> dict[int, Decimal]:
        return await _sum_from_allocation_or_flow(
            db, DIM_TASK, "task_id", task_ids, None, None,
        )

    @staticmethod
    async def get_waybill_energy_cost(
        db: AsyncSession,
        waybill_ids: Sequence[int],
    ) -> dict[int, Decimal]:
        return await _sum_from_allocation_or_flow(
            db, DIM_WAYBILL, "waybill_id", waybill_ids, None, None,
        )


async def _sum_from_allocation_or_flow(
    db: AsyncSession,
    dimension: str,
    flow_col: str,
    ids: Iterable[int],
    start: Optional[date | datetime],
    end: Optional[date | datetime],
) -> dict[int, Decimal]:
    id_list = [int(x) for x in ids if x]
    if not id_list:
        return {}

    alloc_stmt = (
        select(
            EnergyCostAllocation.dimension_id,
            func.sum(EnergyCostAllocation.amount),
        )
        .where(
            EnergyCostAllocation.is_deleted == 0,
            EnergyCostAllocation.dimension == dimension,
            EnergyCostAllocation.dimension_id.in_(id_list),
        )
        .group_by(EnergyCostAllocation.dimension_id)
    )
    if start is not None:
        alloc_stmt = alloc_stmt.where(
            EnergyCostAllocation.period_end >= start if not isinstance(start, datetime)
            else EnergyCostAllocation.period_end >= start.date()
        )
    if end is not None:
        end_d = end.date() if isinstance(end, datetime) else end
        alloc_stmt = alloc_stmt.where(EnergyCostAllocation.period_start <= end_d)

    rows = (await db.execute(alloc_stmt)).all()
    if rows:
        return {int(i): Decimal(a or 0) for i, a in rows}

    col = getattr(EnergyConsumption, flow_col)
    flow = select(col, func.sum(EnergyConsumption.amount)).where(
        EnergyConsumption.is_deleted == 0,
        EnergyConsumption.is_ledger_affecting == 1,
        col.in_(id_list),
    )
    if start is not None:
        flow = flow.where(EnergyConsumption.consumption_time >= _as_dt_start(start))
    if end is not None:
        flow = flow.where(EnergyConsumption.consumption_time <= _as_dt_end(end))
    flow = flow.group_by(col)
    return {int(i): Decimal(a or 0) for i, a in (await db.execute(flow)).all()}
