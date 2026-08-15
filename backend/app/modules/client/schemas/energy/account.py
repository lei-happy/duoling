from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class EnergyAccountCreate(BaseModel):
    accountCode: Optional[str] = None
    accountName: str
    supplierId: int
    energyType: str
    accountType: str = "PREPAID"
    externalAccountNo: Optional[str] = None
    remark: Optional[str] = None


class EnergyAccountUpdate(BaseModel):
    accountName: Optional[str] = None
    energyType: Optional[str] = None
    accountType: Optional[str] = None
    externalAccountNo: Optional[str] = None
    supplierBalance: Optional[Decimal] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class EnergyAccountOut(BaseModel):
    id: int
    accountCode: str
    accountName: str
    supplierId: int
    supplierName: Optional[str] = None
    energyType: str
    accountType: str
    externalAccountNo: Optional[str] = None
    ledgerBalance: Decimal
    supplierBalance: Optional[Decimal] = None
    frozenAmount: Decimal
    availableBalance: Decimal
    diffAmount: Optional[Decimal] = None
    status: int
    lastSyncTime: Optional[datetime] = None
    lastTxnAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: datetime
    cardCount: int = 0

    @classmethod
    def from_model(cls, m, *, supplier_name: Optional[str] = None, card_count: int = 0) -> "EnergyAccountOut":
        return cls(
            id=m.id,
            accountCode=m.account_code,
            accountName=m.account_name,
            supplierId=m.supplier_id,
            supplierName=supplier_name,
            energyType=m.energy_type,
            accountType=m.account_type,
            externalAccountNo=m.external_account_no,
            ledgerBalance=m.ledger_balance,
            supplierBalance=m.supplier_balance,
            frozenAmount=m.frozen_amount,
            availableBalance=m.available_balance,
            diffAmount=m.diff_amount,
            status=m.status,
            lastSyncTime=m.last_sync_time,
            lastTxnAt=m.last_txn_at,
            remark=m.remark,
            createdAt=m.created_at,
            cardCount=card_count,
        )


class EnergyTxnOut(BaseModel):
    id: int
    accountId: int
    txnNo: str
    txnType: int
    amount: Decimal
    delta: Decimal
    frozenDelta: Decimal
    balanceBefore: Decimal
    balanceAfter: Decimal
    bizType: Optional[str] = None
    bizId: Optional[int] = None
    transactionTime: datetime
    remark: Optional[str] = None
    createdAt: datetime

    @classmethod
    def from_model(cls, m) -> "EnergyTxnOut":
        return cls(
            id=m.id,
            accountId=m.account_id,
            txnNo=m.txn_no,
            txnType=m.txn_type,
            amount=m.amount,
            delta=m.delta,
            frozenDelta=m.frozen_delta,
            balanceBefore=m.balance_before,
            balanceAfter=m.balance_after,
            bizType=m.biz_type,
            bizId=m.biz_id,
            transactionTime=m.transaction_time,
            remark=m.remark,
            createdAt=m.created_at,
        )


class EnergyAdjustIn(BaseModel):
    amount: Decimal
    remark: str
