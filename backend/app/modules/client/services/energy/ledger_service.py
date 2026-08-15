"""能源账户记账内核

账户账面余额只能由本服务写入的 append-only 流水改变。
写入时 ``SELECT ... FOR UPDATE`` 锁账户行；记错只能反向冲正，不允许改流水。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.account_txn import EnergyAccountTxn
from app.modules.client.services.energy.constants import (
    ACCOUNT_PREPAID,
    NEGATIVE_BALANCE_ACCOUNT_TYPES,
    STATUS_CLOSED,
    STATUS_DISABLED,
    STATUS_FROZEN,
    STATUS_NORMAL,
    TXN_REVERSAL,
    compute_frozen_delta,
    compute_ledger_delta,
    reversal_deltas,
)

_TXN_NO_PREFIX = "EN"
_TXN_NO_SEQ_WIDTH = 4


class EnergyLedgerService:
    """能源账户记账"""

    @staticmethod
    async def lock_account(db: AsyncSession, account_id: int) -> EnergyAccount:
        r = await db.execute(
            select(EnergyAccount)
            .where(EnergyAccount.id == account_id, EnergyAccount.is_deleted == 0)
            .with_for_update()
        )
        acc = r.scalar_one_or_none()
        if acc is None:
            raise BizException("能源账户不存在")
        return acc

    @staticmethod
    def assert_account_writable(acc: EnergyAccount, *, allow_frozen: bool = False) -> None:
        if acc.status == STATUS_CLOSED:
            raise BizException("账户已关闭，不能记账")
        if acc.status == STATUS_DISABLED:
            raise BizException("账户已停用，不能记账")
        if acc.status == STATUS_FROZEN and not allow_frozen:
            raise BizException("账户已冻结，不能记账")

    @classmethod
    async def post(
        cls,
        db: AsyncSession,
        *,
        account_id: int,
        txn_type: int,
        amount: Decimal,
        transaction_time: Optional[datetime] = None,
        biz_type: Optional[str] = None,
        biz_id: Optional[int] = None,
        external_txn_id: Optional[str] = None,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
        allow_frozen: bool = False,
        signed_delta: Optional[Decimal] = None,
    ) -> EnergyAccountTxn:
        """记账。``signed_delta`` 仅调账/冲正使用（带符号）。"""
        if amount is None:
            raise BizException("请填写金额")
        amount = Decimal(amount)
        if amount <= 0 and signed_delta is None:
            raise BizException("金额必须大于 0")

        acc = await cls.lock_account(db, account_id)
        cls.assert_account_writable(acc, allow_frozen=allow_frozen)

        if signed_delta is not None:
            ledger_delta = Decimal(signed_delta)
            frozen_delta = Decimal("0")
        else:
            ledger_delta = compute_ledger_delta(txn_type, amount)
            frozen_delta = compute_frozen_delta(txn_type, amount)

        return await cls._write(
            db, acc,
            txn_type=txn_type,
            amount=amount.copy_abs() if amount != 0 else ledger_delta.copy_abs(),
            ledger_delta=ledger_delta,
            frozen_delta=frozen_delta,
            transaction_time=transaction_time or datetime.now(),
            biz_type=biz_type,
            biz_id=biz_id,
            external_txn_id=external_txn_id,
            operator_id=operator_id,
            operator_name=operator_name,
            remark=remark,
        )

    @classmethod
    async def reverse(
        cls,
        db: AsyncSession,
        *,
        txn_id: int,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> EnergyAccountTxn:
        """冲正：对原流水记一笔反向流水。同一原流水只能冲正一次。"""
        r = await db.execute(
            select(EnergyAccountTxn).where(
                EnergyAccountTxn.id == txn_id,
                EnergyAccountTxn.is_deleted == 0,
            )
        )
        origin = r.scalar_one_or_none()
        if origin is None:
            raise BizException("原流水不存在")
        if origin.txn_type == TXN_REVERSAL:
            raise BizException("冲正流水不能再次冲正")

        existed = (
            await db.execute(
                select(EnergyAccountTxn.id).where(
                    EnergyAccountTxn.reversed_txn_id == txn_id,
                    EnergyAccountTxn.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if existed:
            raise BizException("该流水已经冲正过，请勿重复操作")

        rev_ledger, rev_frozen = reversal_deltas(origin.delta, origin.frozen_delta)
        acc = await cls.lock_account(db, origin.account_id)
        cls.assert_account_writable(acc, allow_frozen=True)

        txn = await cls._write(
            db, acc,
            txn_type=TXN_REVERSAL,
            amount=origin.amount,
            ledger_delta=rev_ledger,
            frozen_delta=rev_frozen,
            transaction_time=datetime.now(),
            biz_type="reversal",
            biz_id=origin.id,
            operator_id=operator_id,
            operator_name=operator_name,
            remark=remark or f"冲正流水 {origin.txn_no}",
        )
        txn.reversed_txn_id = origin.id
        await db.flush()
        return txn

    @classmethod
    async def _write(
        cls,
        db: AsyncSession,
        acc: EnergyAccount,
        *,
        txn_type: int,
        amount: Decimal,
        ledger_delta: Decimal,
        frozen_delta: Decimal,
        transaction_time: datetime,
        biz_type: Optional[str],
        biz_id: Optional[int],
        external_txn_id: Optional[str] = None,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> EnergyAccountTxn:
        before = acc.ledger_balance or Decimal("0")
        after = before + ledger_delta
        frozen_after = (acc.frozen_amount or Decimal("0")) + frozen_delta

        if frozen_after < 0:
            raise BizException("解冻金额不能超过当前冻结金额")

        if after < 0 and (acc.account_type or ACCOUNT_PREPAID) not in NEGATIVE_BALANCE_ACCOUNT_TYPES:
            raise BizException("账户余额不足，无法完成本次记账")

        txn = EnergyAccountTxn(
            account_id=acc.id,
            txn_no=await cls._generate_txn_no(db),
            txn_type=txn_type,
            amount=amount.copy_abs(),
            delta=ledger_delta,
            frozen_delta=frozen_delta,
            balance_before=before,
            balance_after=after,
            external_txn_id=external_txn_id,
            biz_type=biz_type,
            biz_id=biz_id,
            transaction_time=transaction_time,
            operator_id=operator_id,
            operator_name=operator_name,
            remark=remark,
        )
        db.add(txn)
        acc.ledger_balance = after
        acc.frozen_amount = frozen_after
        acc.last_txn_at = transaction_time
        if acc.status == STATUS_NORMAL or acc.status == STATUS_FROZEN:
            pass
        await db.flush()
        await db.refresh(txn)
        return txn

    @staticmethod
    async def _generate_txn_no(db: AsyncSession) -> str:
        prefix = f"{_TXN_NO_PREFIX}{datetime.now().strftime('%Y%m%d')}"
        r = await db.execute(
            select(func.max(EnergyAccountTxn.txn_no)).where(
                EnergyAccountTxn.txn_no.like(f"{prefix}%")
            )
        )
        last = r.scalar()
        seq = 1
        if last:
            try:
                seq = int(str(last)[len(prefix):]) + 1
            except (TypeError, ValueError):
                seq = 1
        return f"{prefix}{seq:0{_TXN_NO_SEQ_WIDTH}d}"
