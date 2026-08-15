"""能源成本归集：按维度 + 日刷新"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.consumption import EnergyConsumption
from app.modules.client.models.energy.cost_allocation import EnergyCostAllocation
from app.modules.client.services.energy.constants import (
    DIM_DRIVER,
    DIM_SUPPLIER,
    DIM_TASK,
    DIM_VEHICLE,
    DIM_WAYBILL,
)


_DIM_COL = {
    DIM_VEHICLE: EnergyConsumption.vehicle_id,
    DIM_DRIVER: EnergyConsumption.driver_id,
    DIM_TASK: EnergyConsumption.task_id,
    DIM_WAYBILL: EnergyConsumption.waybill_id,
    DIM_SUPPLIER: EnergyConsumption.supplier_id,
}


class EnergyAllocationService:

    @staticmethod
    async def refresh_day(db: AsyncSession, day: date) -> int:
        start = datetime(day.year, day.month, day.day)
        end = start + timedelta(days=1)
        await db.execute(
            delete(EnergyCostAllocation).where(
                EnergyCostAllocation.period_start == day,
                EnergyCostAllocation.period_end == day,
            )
        )
        written = 0
        for dim, col in _DIM_COL.items():
            rows = (await db.execute(
                select(
                    col,
                    EnergyConsumption.energy_type,
                    func.sum(EnergyConsumption.amount),
                    func.sum(EnergyConsumption.quantity),
                    func.sum(EnergyConsumption.mileage),
                    func.count(),
                ).where(
                    EnergyConsumption.is_deleted == 0,
                    EnergyConsumption.is_ledger_affecting == 1,
                    EnergyConsumption.consumption_time >= start,
                    EnergyConsumption.consumption_time < end,
                    col.is_not(None),
                ).group_by(col, EnergyConsumption.energy_type)
            )).all()
            for dim_id, energy_type, amount, qty, mileage, cnt in rows:
                db.add(EnergyCostAllocation(
                    dimension=dim,
                    dimension_id=int(dim_id),
                    period_start=day,
                    period_end=day,
                    energy_type=energy_type,
                    amount=amount or Decimal("0"),
                    quantity=qty or Decimal("0"),
                    mileage=mileage or Decimal("0"),
                    record_count=int(cnt or 0),
                ))
                written += 1
        await db.flush()
        return written
