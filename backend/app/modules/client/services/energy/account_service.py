"""能源账户"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.account_txn import EnergyAccountTxn
from app.modules.client.models.energy.card import EnergyCard
from app.modules.client.models.energy.supplier import EnergySupplier
from app.modules.client.schemas.energy.account import (
    EnergyAccountCreate,
    EnergyAccountOut,
    EnergyAccountUpdate,
    EnergyAdjustIn,
    EnergyTxnOut,
)
from app.modules.client.services.energy.code_util import next_code
from app.modules.client.services.energy.constants import (
    ENERGY_TYPES,
    STATUS_NORMAL,
    TXN_ADJUSTMENT,
)
from app.modules.client.services.energy.ledger_service import EnergyLedgerService
from app.modules.client.services.energy.supplier_service import EnergySupplierService


class EnergyAccountService:

    @staticmethod
    async def page(db, page=1, page_size=20, keyword=None, supplier_id=None,
                   energy_type=None, status=None):
        stmt = select(EnergyAccount).where(EnergyAccount.is_deleted == 0)
        if keyword:
            stmt = stmt.where(
                (EnergyAccount.account_code.contains(keyword))
                | (EnergyAccount.account_name.contains(keyword))
            )
        if supplier_id:
            stmt = stmt.where(EnergyAccount.supplier_id == supplier_id)
        if energy_type:
            stmt = stmt.where(EnergyAccount.energy_type == energy_type)
        if status is not None:
            stmt = stmt.where(EnergyAccount.status == status)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = list((await db.execute(
            stmt.order_by(EnergyAccount.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all())

        supplier_ids = {r.supplier_id for r in rows}
        names = {}
        if supplier_ids:
            for s in (await db.execute(
                select(EnergySupplier).where(EnergySupplier.id.in_(list(supplier_ids)))
            )).scalars().all():
                names[s.id] = s.supplier_name
        card_counts: dict[int, int] = {}
        if rows:
            for aid, cnt in (await db.execute(
                select(EnergyCard.account_id, func.count()).where(
                    EnergyCard.account_id.in_([r.id for r in rows]),
                    EnergyCard.is_deleted == 0,
                ).group_by(EnergyCard.account_id)
            )).all():
                card_counts[int(aid)] = int(cnt)

        return {
            "list": [
                EnergyAccountOut.from_model(
                    r, supplier_name=names.get(r.supplier_id),
                    card_count=card_counts.get(r.id, 0),
                ).model_dump()
                for r in rows
            ],
            "count": total,
        }

    @staticmethod
    async def get(db: AsyncSession, aid: int) -> EnergyAccount:
        r = await db.execute(
            select(EnergyAccount).where(EnergyAccount.id == aid, EnergyAccount.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("能源账户不存在")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: EnergyAccountCreate) -> EnergyAccount:
        await EnergySupplierService.get(db, data.supplierId)
        if data.energyType not in {x["value"] for x in ENERGY_TYPES}:
            raise BizException("请选择正确的能源类型")
        name = (data.accountName or "").strip()
        if not name:
            raise BizException("请填写账户名称")
        code = (data.accountCode or "").strip() or await next_code(
            db, EnergyAccount, "account_code", "EA"
        )
        exists = (await db.execute(
            select(EnergyAccount.id).where(EnergyAccount.account_code == code)
        )).scalar_one_or_none()
        if exists:
            raise BizException("账户编码已存在")
        obj = EnergyAccount(
            account_code=code,
            account_name=name,
            supplier_id=data.supplierId,
            energy_type=data.energyType,
            account_type=data.accountType or "PREPAID",
            external_account_no=data.externalAccountNo,
            remark=data.remark,
            status=STATUS_NORMAL,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, aid: int, data: EnergyAccountUpdate) -> EnergyAccount:
        obj = await EnergyAccountService.get(db, aid)
        payload = data.model_dump(exclude_unset=True)
        mapping = {
            "accountName": "account_name",
            "energyType": "energy_type",
            "accountType": "account_type",
            "externalAccountNo": "external_account_no",
            "supplierBalance": "supplier_balance",
            "status": "status",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k in payload:
                setattr(obj, col, payload[k])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db: AsyncSession, aid: int) -> None:
        obj = await EnergyAccountService.get(db, aid)
        if (obj.ledger_balance or 0) != 0 or (obj.frozen_amount or 0) != 0:
            raise BizException("账户仍有余额或冻结金额，请先结清再删除")
        obj.is_deleted = 1
        await db.flush()

    @staticmethod
    async def page_txns(db, account_id, page=1, page_size=20, txn_type=None):
        await EnergyAccountService.get(db, account_id)
        stmt = select(EnergyAccountTxn).where(
            EnergyAccountTxn.account_id == account_id,
            EnergyAccountTxn.is_deleted == 0,
        )
        if txn_type is not None:
            stmt = stmt.where(EnergyAccountTxn.txn_type == txn_type)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyAccountTxn.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {
            "list": [EnergyTxnOut.from_model(x).model_dump() for x in rows],
            "count": total,
        }

    @staticmethod
    async def adjust(db, account_id: int, data: EnergyAdjustIn, operator_id=None, operator_name=None):
        if not data.remark or len(data.remark.strip()) < 5:
            raise BizException("调账必须填写不少于 5 个字的原因")
        if data.amount == 0:
            raise BizException("调账金额不能为 0")
        return await EnergyLedgerService.post(
            db,
            account_id=account_id,
            txn_type=TXN_ADJUSTMENT,
            amount=data.amount,
            signed_delta=Decimal(data.amount),
            biz_type="manual_adjust",
            operator_id=operator_id,
            operator_name=operator_name,
            remark=data.remark.strip(),
        )
