"""
驾驶员资金账户（往来账）Schemas
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class DriverFundAccountOut(BaseModel):
    """资金账户响应"""
    id: int
    driverId: int
    enterpriseId: Optional[int] = None
    balance: Decimal
    frozenAmount: Decimal
    totalIn: Decimal
    totalOut: Decimal
    status: int
    lastTxnAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_model(cls, m) -> "DriverFundAccountOut":
        return cls(
            id=m.id,
            driverId=m.driver_id,
            enterpriseId=m.enterprise_id,
            balance=m.balance,
            frozenAmount=m.frozen_amount,
            totalIn=m.total_in,
            totalOut=m.total_out,
            status=m.status,
            lastTxnAt=m.last_txn_at,
            remark=m.remark,
            createdAt=m.created_at,
            updatedAt=m.updated_at,
        )


class DriverFundTransactionCreate(BaseModel):
    """财务记账（第 1 期仅支持 bizType 1~5）"""
    bizType: int = Field(..., description="1-预付登记 2-退款入账 3-人工入账 4-人工出账 5-人工调整")
    amount: Decimal = Field(..., gt=0, description="金额（正数）")
    direction: Optional[int] = Field(
        default=None, description="方向 1-入 2-出（仅 bizType=5 人工调整时必填）"
    )
    relatedTaskId: Optional[int] = None
    relatedFinanceDocId: Optional[int] = None
    voucherUrl: Optional[str] = None
    remark: Optional[str] = None


class DriverFundTransactionOut(BaseModel):
    """资金流水响应"""
    id: int
    accountId: int
    driverId: int
    enterpriseId: Optional[int] = None
    txnNo: str
    bizType: int
    direction: int
    amount: Decimal
    delta: Decimal
    balanceBefore: Decimal
    balanceAfter: Decimal
    relatedTaskId: Optional[int] = None
    relatedFinanceDocId: Optional[int] = None
    source: int
    operatorId: Optional[int] = None
    operatorName: Optional[str] = None
    voucherUrl: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime

    @classmethod
    def from_model(cls, m) -> "DriverFundTransactionOut":
        return cls(
            id=m.id,
            accountId=m.account_id,
            driverId=m.driver_id,
            enterpriseId=m.enterprise_id,
            txnNo=m.txn_no,
            bizType=m.biz_type,
            direction=m.direction,
            amount=m.amount,
            delta=m.delta,
            balanceBefore=m.balance_before,
            balanceAfter=m.balance_after,
            relatedTaskId=m.related_task_id,
            relatedFinanceDocId=m.related_finance_doc_id,
            source=m.source,
            operatorId=m.operator_id,
            operatorName=m.operator_name,
            voucherUrl=m.voucher_url,
            remark=m.remark,
            createdAt=m.created_at,
        )


class DriverFundAccountStatusUpdate(BaseModel):
    """冻结 / 解冻"""
    status: int = Field(..., description="1-正常 0-冻结")
