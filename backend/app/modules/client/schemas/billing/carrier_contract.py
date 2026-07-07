"""
承运商合同 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class CarrierContractCreate(BaseModel):
    contractNo: str
    contractName: str
    carrierId: int
    carrierName: Optional[str] = None
    effectiveDate: date
    expiryDate: date
    remark: Optional[str] = None


class CarrierContractUpdate(BaseModel):
    contractName: Optional[str] = None
    carrierId: Optional[int] = None
    carrierName: Optional[str] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class CarrierContractOut(BaseModel):
    id: int
    contractNo: str
    contractName: str
    carrierId: int
    carrierName: Optional[str] = None
    effectiveDate: date
    expiryDate: date
    status: int
    remark: Optional[str] = None
    createdAt: datetime
    # 当前在有效期内且启用、可参与匹配的承运价条数（相对服务端当天日期）
    activeRateCount: int = 0
    # 未删除的承运价总条数
    totalRateCount: int = 0

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "CarrierContractOut":
        return cls(
            id=m.id,
            contractNo=m.contract_no,
            contractName=m.contract_name,
            carrierId=m.carrier_id,
            carrierName=m.carrier_name,
            effectiveDate=m.effective_date,
            expiryDate=m.expiry_date,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
