"""能源对账：账户余额对账 + 消费流水对账"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.consumption import EnergyConsumption
from app.modules.client.models.energy.recon import EnergyRecon
from app.modules.client.models.energy.recon_item import EnergyReconItem
from app.modules.client.services.energy.account_service import EnergyAccountService
from app.modules.client.services.energy.code_util import next_code
from app.modules.client.services.energy.constants import (
    DOC_DRAFT,
    DOC_KIND_RECON,
    DOC_REVIEWED,
    DOC_SETTLED,
    RECON_AMOUNT_DIFF,
    RECON_MATCHED,
    RECON_MISSING_EXTERNAL,
    RECON_MISSING_INTERNAL,
    RECON_TYPE_BALANCE,
    RECON_TYPE_CONSUMPTION,
)
from app.modules.client.services.finance.base.constants import FinanceDirection


class EnergyReconService:

    @staticmethod
    async def page(db, page=1, page_size=20, account_id=None, status=None):
        stmt = select(EnergyRecon).where(EnergyRecon.is_deleted == 0)
        if account_id:
            stmt = stmt.where(EnergyRecon.account_id == account_id)
        if status is not None:
            stmt = stmt.where(EnergyRecon.status == status)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyRecon.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {"list": [_recon_out(x) for x in rows], "count": total}

    @staticmethod
    async def get(db, rid: int) -> EnergyRecon:
        r = await db.execute(
            select(EnergyRecon).where(EnergyRecon.id == rid, EnergyRecon.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("对账单不存在")
        return obj

    @staticmethod
    async def create_balance_recon(
        db, account_id: int, supplier_balance: Decimal, created_by=None,
    ) -> EnergyRecon:
        acc = await EnergyAccountService.get(db, account_id)
        acc.supplier_balance = supplier_balance
        diff = (acc.ledger_balance or Decimal("0")) - Decimal(supplier_balance)
        obj = EnergyRecon(
            doc_no=await next_code(db, EnergyRecon, "doc_no", "EQ"),
            doc_kind=DOC_KIND_RECON,
            status=DOC_DRAFT,
            direction=FinanceDirection.PAY,
            planned_amount=abs(diff),
            account_id=account_id,
            supplier_id=acc.supplier_id,
            recon_type=RECON_TYPE_BALANCE,
            external_amount=Decimal(supplier_balance),
            internal_amount=acc.ledger_balance or Decimal("0"),
            difference_amount=diff,
            created_by=created_by,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def create_consumption_recon(
        db,
        *,
        account_id: Optional[int],
        supplier_id: Optional[int],
        start: datetime,
        end: datetime,
        external_rows: list[dict],
        created_by=None,
    ) -> EnergyRecon:
        stmt = select(EnergyConsumption).where(
            EnergyConsumption.is_deleted == 0,
            EnergyConsumption.consumption_time >= start,
            EnergyConsumption.consumption_time <= end,
        )
        if account_id:
            stmt = stmt.where(EnergyConsumption.account_id == account_id)
        if supplier_id:
            stmt = stmt.where(EnergyConsumption.supplier_id == supplier_id)
        internals = list((await db.execute(stmt)).scalars().all())

        ext_by_id: dict[str, dict] = {}
        for row in external_rows:
            key = str(row.get("externalTransactionId") or row.get("流水号") or "").strip()
            if not key:
                key = f"anon:{len(ext_by_id)}"
            ext_by_id[key] = row

        int_by_id = {}
        unmatched_int = []
        for c in internals:
            if c.external_transaction_id:
                int_by_id[str(c.external_transaction_id)] = c
            else:
                unmatched_int.append(c)

        items: list[EnergyReconItem] = []
        matched = 0
        diffs = 0
        ext_sum = Decimal("0")
        int_sum = Decimal("0")

        used_int: set[int] = set()
        for key, row in ext_by_id.items():
            ext_amt = Decimal(str(row.get("amount") or row.get("金额") or 0))
            ext_sum += ext_amt
            c = int_by_id.get(key)
            if c is None:
                items.append(EnergyReconItem(
                    external_transaction_id=key if not key.startswith("anon:") else None,
                    external_amount=ext_amt,
                    recon_result=RECON_MISSING_INTERNAL,
                ))
                diffs += 1
                continue
            used_int.add(c.id)
            int_sum += c.amount or Decimal("0")
            result = RECON_MATCHED if (c.amount or 0) == ext_amt else RECON_AMOUNT_DIFF
            if result == RECON_MATCHED:
                matched += 1
                c.recon_status = RECON_MATCHED
            else:
                diffs += 1
                c.recon_status = RECON_AMOUNT_DIFF
            items.append(EnergyReconItem(
                consumption_id=c.id,
                external_transaction_id=key,
                external_amount=ext_amt,
                internal_amount=c.amount,
                difference_amount=(c.amount or 0) - ext_amt,
                recon_result=result,
            ))

        for c in internals:
            if c.id in used_int:
                continue
            int_sum += c.amount or Decimal("0")
            c.recon_status = RECON_MISSING_EXTERNAL
            items.append(EnergyReconItem(
                consumption_id=c.id,
                internal_amount=c.amount,
                recon_result=RECON_MISSING_EXTERNAL,
            ))
            diffs += 1

        obj = EnergyRecon(
            doc_no=await next_code(db, EnergyRecon, "doc_no", "EQ"),
            doc_kind=DOC_KIND_RECON,
            status=DOC_DRAFT,
            direction=FinanceDirection.PAY,
            planned_amount=abs(ext_sum - int_sum),
            period_start=start,
            period_end=end,
            account_id=account_id,
            supplier_id=supplier_id,
            recon_type=RECON_TYPE_CONSUMPTION,
            external_amount=ext_sum,
            internal_amount=int_sum,
            difference_amount=ext_sum - int_sum,
            matched_count=matched,
            diff_count=diffs,
            created_by=created_by,
        )
        db.add(obj)
        await db.flush()
        for it in items:
            it.recon_id = obj.id
            db.add(it)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def items(db, rid: int):
        await EnergyReconService.get(db, rid)
        rows = (await db.execute(
            select(EnergyReconItem).where(
                EnergyReconItem.recon_id == rid, EnergyReconItem.is_deleted == 0
            ).order_by(EnergyReconItem.id.asc())
        )).scalars().all()
        return [_item_out(x) for x in rows]

    @staticmethod
    async def confirm_item(db, item_id: int, process_status: str = "confirmed"):
        r = await db.execute(
            select(EnergyReconItem).where(
                EnergyReconItem.id == item_id, EnergyReconItem.is_deleted == 0
            )
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("对账明细不存在")
        obj.process_status = process_status
        await db.flush()
        return obj

    @staticmethod
    async def settle(db, rid: int) -> EnergyRecon:
        obj = await EnergyReconService.get(db, rid)
        pending = (await db.execute(
            select(func.count()).select_from(EnergyReconItem).where(
                EnergyReconItem.recon_id == rid,
                EnergyReconItem.is_deleted == 0,
                EnergyReconItem.recon_result != RECON_MATCHED,
                EnergyReconItem.process_status == "pending",
            )
        )).scalar() or 0
        if pending:
            raise BizException(f"还有 {pending} 笔差异未处理，请先确认或忽略")
        obj.status = DOC_SETTLED
        await db.flush()
        return obj


def _recon_out(m: EnergyRecon) -> dict:
    return {
        "id": m.id,
        "docNo": m.doc_no,
        "accountId": m.account_id,
        "supplierId": m.supplier_id,
        "reconType": m.recon_type,
        "periodStart": m.period_start,
        "periodEnd": m.period_end,
        "externalAmount": m.external_amount,
        "internalAmount": m.internal_amount,
        "differenceAmount": m.difference_amount,
        "matchedCount": m.matched_count,
        "diffCount": m.diff_count,
        "status": m.status,
        "createdAt": m.created_at,
    }


def _item_out(m: EnergyReconItem) -> dict:
    return {
        "id": m.id,
        "reconId": m.recon_id,
        "consumptionId": m.consumption_id,
        "externalTransactionId": m.external_transaction_id,
        "externalAmount": m.external_amount,
        "internalAmount": m.internal_amount,
        "differenceAmount": m.difference_amount,
        "reconResult": m.recon_result,
        "processStatus": m.process_status,
        "remark": m.remark,
    }
