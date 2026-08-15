"""每日余额快照"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.account_daily_snapshot import EnergyAccountDailySnapshot
from app.modules.client.models.energy.account_txn import EnergyAccountTxn
from app.modules.client.services.energy.constants import (
    TXN_ADJUSTMENT,
    TXN_CONSUMPTION,
    TXN_RECHARGE,
    TXN_REFUND,
)


class EnergySnapshotService:

    @staticmethod
    async def build_day(db: AsyncSession, day: date) -> int:
        start = datetime(day.year, day.month, day.day)
        end = start + timedelta(days=1)
        accounts = (await db.execute(
            select(EnergyAccount).where(EnergyAccount.is_deleted == 0)
        )).scalars().all()
        written = 0
        for acc in accounts:
            existed = (await db.execute(
                select(EnergyAccountDailySnapshot).where(
                    EnergyAccountDailySnapshot.account_id == acc.id,
                    EnergyAccountDailySnapshot.snapshot_date == day,
                    EnergyAccountDailySnapshot.is_deleted == 0,
                )
            )).scalar_one_or_none()
            sums = {TXN_RECHARGE: Decimal("0"), TXN_CONSUMPTION: Decimal("0"),
                    TXN_REFUND: Decimal("0"), TXN_ADJUSTMENT: Decimal("0")}
            rows = (await db.execute(
                select(EnergyAccountTxn.txn_type, func.sum(EnergyAccountTxn.delta)).where(
                    EnergyAccountTxn.account_id == acc.id,
                    EnergyAccountTxn.is_deleted == 0,
                    EnergyAccountTxn.transaction_time >= start,
                    EnergyAccountTxn.transaction_time < end,
                ).group_by(EnergyAccountTxn.txn_type)
            )).all()
            day_delta = Decimal("0")
            for t, d in rows:
                day_delta += Decimal(d or 0)
                if t in sums:
                    if t == TXN_ADJUSTMENT:
                        sums[t] = Decimal(d or 0)
                    else:
                        sums[t] = abs(Decimal(d or 0))
            closing = acc.ledger_balance or Decimal("0")
            # 当日快照时账户已是当前余额；历史日用「当前余额 - 之后发生额」近似
            if day < date.today():
                after = (await db.execute(
                    select(func.coalesce(func.sum(EnergyAccountTxn.delta), 0)).where(
                        EnergyAccountTxn.account_id == acc.id,
                        EnergyAccountTxn.is_deleted == 0,
                        EnergyAccountTxn.transaction_time >= end,
                    )
                )).scalar() or 0
                closing = (acc.ledger_balance or Decimal("0")) - Decimal(after)
            opening = closing - day_delta
            if existed:
                snap = existed
            else:
                snap = EnergyAccountDailySnapshot(account_id=acc.id, snapshot_date=day)
                db.add(snap)
            snap.opening_balance = opening
            snap.recharge_amount = sums[TXN_RECHARGE]
            snap.consumption_amount = sums[TXN_CONSUMPTION]
            snap.refund_amount = sums[TXN_REFUND]
            snap.adjustment_amount = sums[TXN_ADJUSTMENT]
            snap.closing_balance = closing
            snap.supplier_balance = acc.supplier_balance
            snap.frozen_amount = acc.frozen_amount or Decimal("0")
            written += 1
        await db.flush()
        return written
