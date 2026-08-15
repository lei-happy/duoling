from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class EnergyRechargeCreate(BaseModel):
    accountId: int
    plannedAmount: Decimal
    rechargeTime: Optional[datetime] = None
    payMethod: Optional[int] = None
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = None
    paymentReference: Optional[str] = None
    payVoucherUrl: Optional[str] = None
    remark: Optional[str] = None


class EnergyRechargeOut(BaseModel):
    id: int
    docNo: str
    accountId: int
    accountName: Optional[str] = None
    supplierId: Optional[int] = None
    plannedAmount: Decimal
    actualAmount: Optional[Decimal] = None
    status: int
    rechargeTime: Optional[datetime] = None
    payMethod: Optional[int] = None
    bankAccountLabel: Optional[str] = None
    paymentReference: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime

    @classmethod
    def from_model(cls, m, *, account_name: Optional[str] = None) -> "EnergyRechargeOut":
        return cls(
            id=m.id,
            docNo=m.doc_no,
            accountId=m.account_id,
            accountName=account_name,
            supplierId=m.supplier_id,
            plannedAmount=m.planned_amount,
            actualAmount=m.actual_amount,
            status=m.status,
            rechargeTime=m.recharge_time,
            payMethod=m.pay_method,
            bankAccountLabel=m.bank_account_label,
            paymentReference=m.payment_reference,
            remark=m.remark,
            createdAt=m.created_at,
        )


class EnergyRechargePayIn(BaseModel):
    actualAmount: Optional[Decimal] = None
    payMethod: Optional[int] = None
    bankAccountId: Optional[int] = None
    bankAccountLabel: Optional[str] = None
    paymentReference: Optional[str] = None
    payVoucherUrl: Optional[str] = None
