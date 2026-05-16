"""
运价合同 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class FreightContractCreate(BaseModel):
    contractNo: str
    contractName: str
    customerId: int
    customerName: Optional[str] = None
    effectiveDate: date
    expiryDate: date
    remark: Optional[str] = None


class FreightContractUpdate(BaseModel):
    contractName: Optional[str] = None
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class FreightContractOut(BaseModel):
    id: int
    contractNo: str
    contractName: str
    customerId: int
    customerName: Optional[str] = None
    effectiveDate: date
    expiryDate: date
    status: int
    remark: Optional[str] = None
    createdAt: datetime
    # 当前在运价有效期内且启用、可参与匹配的运价条数（相对服务端当天日期）
    activeRateCount: int = 0
    # 未删除的运价总条数
    totalRateCount: int = 0

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "FreightContractOut":
        return cls(
            id=m.id,
            contractNo=m.contract_no,
            contractName=m.contract_name,
            customerId=m.customer_id,
            customerName=m.customer_name,
            effectiveDate=m.effective_date,
            expiryDate=m.expiry_date,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
