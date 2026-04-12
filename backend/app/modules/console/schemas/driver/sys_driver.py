"""
平台司机 Schemas
"""

from typing import Optional
from pydantic import BaseModel


class SysDriverOut(BaseModel):
    id: int
    tenantCode: str
    tenantName: Optional[str] = None
    bizDriverId: int
    driverCode: str
    name: str
    phone: str
    status: int
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = {"from_attributes": True}


class SysDriverParam(BaseModel):
    page: int = 1
    limit: int = 20
    keyword: Optional[str] = None
    tenantCode: Optional[str] = None
    status: Optional[int] = None
