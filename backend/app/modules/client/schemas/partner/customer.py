"""
客户管理 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    customerCode: Optional[str] = None
    customerName: str
    shortName: Optional[str] = None
    customerType: Optional[int] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    settlementType: Optional[int] = None
    creditCode: Optional[str] = None
    remark: Optional[str] = None


class CustomerUpdate(BaseModel):
    customerCode: Optional[str] = None
    customerName: Optional[str] = None
    shortName: Optional[str] = None
    customerType: Optional[int] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    settlementType: Optional[int] = None
    creditCode: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    customerCode: Optional[str] = None
    customerName: str
    shortName: Optional[str] = None
    customerType: Optional[int] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    settlementType: Optional[int] = None
    creditCode: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "CustomerOut":
        return cls(
            id=m.id,
            customerCode=m.customer_code,
            customerName=m.customer_name,
            shortName=m.short_name,
            customerType=m.customer_type,
            contactPerson=m.contact_person,
            contactPhone=m.contact_phone,
            address=m.address,
            settlementType=m.settlement_type,
            creditCode=m.credit_code,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
