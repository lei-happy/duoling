"""能源充值单

一期自带「登记付款」：确认后写能源账户充值流水。
# 二期接入点：PayableDocKind + PaymentBatchService._DOC_MODELS / _pay_source_doc
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.recharge import EnergyRecharge
from app.modules.client.schemas.energy.recharge import (
    EnergyRechargeCreate,
    EnergyRechargeOut,
    EnergyRechargePayIn,
)
from app.modules.client.services.energy.account_service import EnergyAccountService
from app.modules.client.services.energy.code_util import next_code
from app.modules.client.services.energy.constants import (
    DOC_CANCELLED,
    DOC_DRAFT,
    DOC_KIND_RECHARGE,
    DOC_PAID,
    DOC_REVIEWED,
    TXN_RECHARGE,
)
from app.modules.client.services.energy.ledger_service import EnergyLedgerService
from app.modules.client.services.finance.base.constants import FinanceDirection


class EnergyRechargeService:
    doc_kind = DOC_KIND_RECHARGE
    doc_no_prefix = "ER"

    @staticmethod
    async def page(db, page=1, page_size=20, keyword=None, account_id=None, status=None):
        stmt = select(EnergyRecharge).where(EnergyRecharge.is_deleted == 0)
        if keyword:
            stmt = stmt.where(EnergyRecharge.doc_no.contains(keyword))
        if account_id:
            stmt = stmt.where(EnergyRecharge.account_id == account_id)
        if status is not None:
            stmt = stmt.where(EnergyRecharge.status == status)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = list((await db.execute(
            stmt.order_by(EnergyRecharge.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all())
        names = {}
        if rows:
            for a in (await db.execute(
                select(EnergyAccount).where(EnergyAccount.id.in_({r.account_id for r in rows}))
            )).scalars().all():
                names[a.id] = a.account_name
        return {
            "list": [
                EnergyRechargeOut.from_model(r, account_name=names.get(r.account_id)).model_dump()
                for r in rows
            ],
            "count": total,
        }

    @staticmethod
    async def get(db: AsyncSession, rid: int) -> EnergyRecharge:
        r = await db.execute(
            select(EnergyRecharge).where(EnergyRecharge.id == rid, EnergyRecharge.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("充值单不存在")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: EnergyRechargeCreate, created_by=None) -> EnergyRecharge:
        acc = await EnergyAccountService.get(db, data.accountId)
        if data.plannedAmount is None or data.plannedAmount <= 0:
            raise BizException("请填写大于 0 的充值金额")
        obj = EnergyRecharge(
            doc_no=await next_code(db, EnergyRecharge, "doc_no", "ER"),
            doc_kind=DOC_KIND_RECHARGE,
            status=DOC_DRAFT,
            direction=FinanceDirection.PAY,
            planned_amount=data.plannedAmount,
            account_id=data.accountId,
            supplier_id=acc.supplier_id,
            recharge_time=data.rechargeTime,
            pay_method=data.payMethod,
            bank_account_id=data.bankAccountId,
            bank_account_label=data.bankAccountLabel,
            payment_reference=data.paymentReference,
            pay_voucher_url=data.payVoucherUrl,
            remark=data.remark,
            created_by=created_by,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def register_pay(
        db: AsyncSession,
        rid: int,
        data: EnergyRechargePayIn,
        operator_id=None,
        operator_name=None,
    ) -> EnergyRecharge:
        """登记付款并入账。一期不进出纳打款批次。"""
        obj = await EnergyRechargeService.get(db, rid)
        if obj.status == DOC_PAID:
            raise BizException("这笔充值已经入账，请勿重复操作")
        if obj.status == DOC_CANCELLED:
            raise BizException("已撤销的充值单不能入账")
        amount = data.actualAmount or obj.planned_amount
        if amount is None or amount <= 0:
            raise BizException("入账金额必须大于 0")
        if data.payMethod is not None:
            obj.pay_method = data.payMethod
        if data.bankAccountId is not None:
            obj.bank_account_id = data.bankAccountId
        if data.bankAccountLabel:
            obj.bank_account_label = data.bankAccountLabel
        if data.paymentReference:
            obj.payment_reference = data.paymentReference
        if data.payVoucherUrl:
            obj.pay_voucher_url = data.payVoucherUrl

        txn = await EnergyLedgerService.post(
            db,
            account_id=obj.account_id,
            txn_type=TXN_RECHARGE,
            amount=Decimal(amount),
            transaction_time=obj.recharge_time or datetime.now(),
            biz_type="recharge",
            biz_id=obj.id,
            operator_id=operator_id,
            operator_name=operator_name,
            remark=f"充值单 {obj.doc_no}",
        )
        obj.actual_amount = amount
        obj.status = DOC_PAID
        obj.paid_by = operator_id
        obj.paid_at = datetime.now()
        obj.ledger_txn_id = txn.id
        if obj.status == DOC_DRAFT:
            obj.status = DOC_PAID
        await db.flush()
        return obj

    @staticmethod
    async def cancel(db: AsyncSession, rid: int, reason: str, operator_id=None, operator_name=None):
        obj = await EnergyRechargeService.get(db, rid)
        if obj.status == DOC_CANCELLED:
            raise BizException("充值单已经撤销")
        if not reason or len(reason.strip()) < 5:
            raise BizException("撤销原因请至少写 5 个字")
        if obj.status == DOC_PAID and obj.ledger_txn_id:
            await EnergyLedgerService.reverse(
                db,
                txn_id=obj.ledger_txn_id,
                operator_id=operator_id,
                operator_name=operator_name,
                remark=f"撤销充值单 {obj.doc_no}",
            )
        obj.status = DOC_CANCELLED
        obj.cancelled_by = operator_id
        obj.cancelled_at = datetime.now()
        obj.cancel_reason = reason.strip()
        await db.flush()
        return obj
