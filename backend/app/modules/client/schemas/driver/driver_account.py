"""
驾驶员账户结算 Schemas
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class DriverAccountCreate(BaseModel):
    """创建账户"""
    accountType: int
    enterpriseId: Optional[int] = None
    accountName: str
    accountNo: str
    status: Optional[int] = 1


class DriverAccountUpdate(BaseModel):
    """更新账户"""
    accountType: Optional[int] = None
    enterpriseId: Optional[int] = None
    accountName: Optional[str] = None
    accountNo: Optional[str] = None
    status: Optional[int] = None


class DriverAccountOut(BaseModel):
    """账户响应"""
    id: int
    driverId: int
    enterpriseId: Optional[int] = None
    accountType: int
    accountName: str
    accountNo: str
    balance: Decimal
    status: int
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "DriverAccountOut":
        return cls(
            id=m.id,
            driverId=m.driver_id,
            enterpriseId=m.enterprise_id,
            accountType=m.account_type,
            accountName=m.account_name,
            accountNo=m.account_no,
            balance=m.balance,
            status=m.status,
            createdAt=m.created_at,
            updatedAt=m.updated_at,
        )
