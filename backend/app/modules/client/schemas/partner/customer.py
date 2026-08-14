"""
客户管理 Schemas
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import CreditStatus

# 「结算与信用」分组：账期天数上界按 1 年，超过一年的账期属异常约定
_PAYMENT_DAYS = Field(
    default=None, ge=0, le=365, description="账期天数，空=未设置（按 0 天算）",
)
_CREDIT_LIMIT = Field(
    default=None, ge=0, description="信用额度，空=不限额；超额只预警不拦截",
)
_CREDIT_STATUS = Field(
    default=None, ge=0, le=2, description="信用状态 0-暂停合作 1-正常 2-重点关注",
)


class CustomerCreate(BaseModel):
    customerCode: Optional[str] = None
    customerName: str
    shortName: Optional[str] = None
    enterpriseId: Optional[int] = None
    customerType: Optional[int] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    settlementType: Optional[int] = None
    paymentDays: Optional[int] = _PAYMENT_DAYS
    creditLimit: Optional[Decimal] = _CREDIT_LIMIT
    creditStatus: Optional[int] = _CREDIT_STATUS
    creditCode: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class CustomerUpdate(BaseModel):
    customerCode: Optional[str] = None
    customerName: Optional[str] = None
    shortName: Optional[str] = None
    enterpriseId: Optional[int] = None
    customerType: Optional[int] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    settlementType: Optional[int] = None
    paymentDays: Optional[int] = _PAYMENT_DAYS
    creditLimit: Optional[Decimal] = _CREDIT_LIMIT
    creditStatus: Optional[int] = _CREDIT_STATUS
    creditCode: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    customerCode: Optional[str] = None
    customerName: str
    shortName: Optional[str] = None
    enterpriseId: Optional[int] = None
    customerType: Optional[int] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    settlementType: Optional[int] = None
    paymentDays: Optional[int] = None
    creditLimit: Optional[float] = None
    creditStatus: int = CreditStatus.NORMAL
    creditStatusLabel: Optional[str] = None
    creditCode: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "CustomerOut":
        credit_status = int(
            m.credit_status if m.credit_status is not None else CreditStatus.NORMAL
        )
        return cls(
            id=m.id,
            customerCode=m.customer_code,
            customerName=m.customer_name,
            shortName=m.short_name,
            enterpriseId=m.enterprise_id,
            customerType=m.customer_type,
            contactPerson=m.contact_person,
            contactPhone=m.contact_phone,
            address=m.address,
            settlementType=m.settlement_type,
            paymentDays=m.payment_days,
            creditLimit=(
                float(m.credit_limit) if m.credit_limit is not None else None
            ),
            creditStatus=credit_status,
            creditStatusLabel=CreditStatus.LABELS.get(credit_status),
            creditCode=m.credit_code,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
