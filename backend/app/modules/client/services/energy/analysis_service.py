"""能源成本 / 资金效率分析

里程分母：优先用消费流水上的 mileage（表显/手工录入）。
任务表目前没有 distance_km，因此不从任务汇总里程。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.account_daily_snapshot import EnergyAccountDailySnapshot
from app.modules.client.models.energy.account_txn import EnergyAccountTxn
from app.modules.client.models.energy.consumption import EnergyConsumption
from app.modules.client.models.energy.cost_allocation import EnergyCostAllocation
from app.modules.client.models.energy.supplier import EnergySupplier
from app.modules.client.services.energy.constants import (
    DIM_SUPPLIER,
    DIM_VEHICLE,
    TXN_CONSUMPTION,
    TXN_RECHARGE,
)


class EnergyAnalysisService:

    @staticmethod
    async def overview(db: AsyncSession) -> dict:
        acc_rows = (await db.execute(
            select(
                func.coalesce(func.sum(EnergyAccount.ledger_balance), 0),
                func.coalesce(func.sum(EnergyAccount.frozen_amount), 0),
                func.count(),
            ).where(EnergyAccount.is_deleted == 0)
        )).one()
        today = date.today()
        month_start = datetime(today.year, today.month, 1)
        month_cons = (await db.execute(
            select(func.coalesce(func.sum(EnergyConsumption.amount), 0)).where(
                EnergyConsumption.is_deleted == 0,
                EnergyConsumption.is_ledger_affecting == 1,
                EnergyConsumption.consumption_time >= month_start,
            )
        )).scalar() or 0
        month_recharge = (await db.execute(
            select(func.coalesce(func.sum(EnergyAccountTxn.amount), 0)).where(
                EnergyAccountTxn.is_deleted == 0,
                EnergyAccountTxn.txn_type == TXN_RECHARGE,
                EnergyAccountTxn.transaction_time >= month_start,
            )
        )).scalar() or 0
        today_cons = (await db.execute(
            select(func.coalesce(func.sum(EnergyConsumption.amount), 0)).where(
                EnergyConsumption.is_deleted == 0,
                EnergyConsumption.is_ledger_affecting == 1,
                EnergyConsumption.consumption_time >= datetime(today.year, today.month, today.day),
            )
        )).scalar() or 0
        unmatched = (await db.execute(
            select(func.count()).select_from(EnergyConsumption).where(
                EnergyConsumption.is_deleted == 0,
                EnergyConsumption.match_status.in_(("UNMATCHED", "PARTIAL")),
            )
        )).scalar() or 0
        ledger = Decimal(acc_rows[0] or 0)
        frozen = Decimal(acc_rows[1] or 0)
        daily_avg = Decimal(month_cons or 0) / Decimal(max(today.day, 1))
        usable_days = (ledger / daily_avg) if daily_avg > 0 else None
        return {
            "accountCount": int(acc_rows[2] or 0),
            "ledgerBalance": ledger,
            "availableBalance": ledger - frozen,
            "frozenAmount": frozen,
            "monthRecharge": Decimal(month_recharge or 0),
            "monthConsumption": Decimal(month_cons or 0),
            "todayConsumption": Decimal(today_cons or 0),
            "usableDays": float(usable_days) if usable_days is not None else None,
            "unmatchedCount": int(unmatched),
            "note": "油补是付给司机的补贴，能源消费是付给供应商的能源费，两笔钱不重复。",
        }

    @staticmethod
    async def vehicle_cost(db, start: date, end: date, limit: int = 20) -> list[dict]:
        rows = (await db.execute(
            select(
                EnergyCostAllocation.dimension_id,
                func.sum(EnergyCostAllocation.amount),
                func.sum(EnergyCostAllocation.quantity),
                func.sum(EnergyCostAllocation.mileage),
            ).where(
                EnergyCostAllocation.is_deleted == 0,
                EnergyCostAllocation.dimension == DIM_VEHICLE,
                EnergyCostAllocation.period_start >= start,
                EnergyCostAllocation.period_end <= end,
            ).group_by(EnergyCostAllocation.dimension_id)
            .order_by(func.sum(EnergyCostAllocation.amount).desc())
            .limit(limit)
        )).all()
        out = []
        for vid, amount, qty, mileage in rows:
            amount = Decimal(amount or 0)
            mileage = Decimal(mileage or 0)
            qty = Decimal(qty or 0)
            out.append({
                "vehicleId": int(vid),
                "amount": amount,
                "quantity": qty,
                "mileage": mileage,
                "costPer100km": (amount / mileage * 100) if mileage > 0 else None,
                "qtyPer100km": (qty / mileage * 100) if mileage > 0 else None,
            })
        return out

    @staticmethod
    async def supplier_compare(db, start: date, end: date) -> list[dict]:
        rows = (await db.execute(
            select(
                EnergyCostAllocation.dimension_id,
                func.sum(EnergyCostAllocation.amount),
                func.sum(EnergyCostAllocation.quantity),
            ).where(
                EnergyCostAllocation.is_deleted == 0,
                EnergyCostAllocation.dimension == DIM_SUPPLIER,
                EnergyCostAllocation.period_start >= start,
                EnergyCostAllocation.period_end <= end,
            ).group_by(EnergyCostAllocation.dimension_id)
        )).all()
        names = {}
        if rows:
            for s in (await db.execute(
                select(EnergySupplier).where(
                    EnergySupplier.id.in_([int(r[0]) for r in rows])
                )
            )).scalars().all():
                names[s.id] = s.supplier_name
        accounts = (await db.execute(
            select(
                EnergyAccount.supplier_id,
                func.sum(EnergyAccount.ledger_balance),
            ).where(EnergyAccount.is_deleted == 0).group_by(EnergyAccount.supplier_id)
        )).all()
        bal = {int(i): Decimal(a or 0) for i, a in accounts}
        out = []
        for sid, amount, qty in rows:
            amount = Decimal(amount or 0)
            qty = Decimal(qty or 0)
            days = max((end - start).days, 1)
            daily = amount / Decimal(days)
            balance = bal.get(int(sid), Decimal("0"))
            out.append({
                "supplierId": int(sid),
                "supplierName": names.get(int(sid)),
                "amount": amount,
                "quantity": qty,
                "avgPrice": (amount / qty) if qty > 0 else None,
                "ledgerBalance": balance,
                "usableDays": float(balance / daily) if daily > 0 else None,
                "idleHint": bool(balance > 0 and daily > 0 and balance / daily > 60),
            })
        return out

    @staticmethod
    async def fund_efficiency(db, account_id: int, days: int = 30) -> dict:
        end = date.today()
        start = end - timedelta(days=days)
        snaps = (await db.execute(
            select(EnergyAccountDailySnapshot).where(
                EnergyAccountDailySnapshot.account_id == account_id,
                EnergyAccountDailySnapshot.snapshot_date >= start,
                EnergyAccountDailySnapshot.snapshot_date <= end,
                EnergyAccountDailySnapshot.is_deleted == 0,
            ).order_by(EnergyAccountDailySnapshot.snapshot_date.asc())
        )).scalars().all()
        if not snaps:
            acc = (await db.execute(
                select(EnergyAccount).where(EnergyAccount.id == account_id)
            )).scalar_one_or_none()
            return {
                "accountId": account_id,
                "avgBalance": acc.ledger_balance if acc else 0,
                "consumption": 0,
                "turnover": None,
                "usableDays": None,
                "snapshots": [],
            }
        avg_bal = sum((s.closing_balance or 0) for s in snaps) / Decimal(len(snaps))
        cons = sum((s.consumption_amount or 0) for s in snaps)
        daily = cons / Decimal(max(len(snaps), 1))
        last = snaps[-1].closing_balance or Decimal("0")
        return {
            "accountId": account_id,
            "avgBalance": avg_bal,
            "consumption": cons,
            "turnover": float(cons / avg_bal) if avg_bal else None,
            "usableDays": float(last / daily) if daily > 0 else None,
            "snapshots": [
                {
                    "date": s.snapshot_date,
                    "opening": s.opening_balance,
                    "recharge": s.recharge_amount,
                    "consumption": s.consumption_amount,
                    "closing": s.closing_balance,
                }
                for s in snaps
            ],
        }
