"""
租户管理 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TenantCreate(BaseModel):
    """创建租户"""
    tenant_name: str
    short_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    license_no: Optional[str] = None
    remark: Optional[str] = None


class TenantUpdate(BaseModel):
    """更新租户"""
    tenant_name: Optional[str] = None
    short_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    license_no: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class TenantOut(BaseModel):
    """租户详情输出"""
    id: int
    tenant_code: str
    tenant_name: str
    short_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    license_no: Optional[str] = None
    status: int
    db_name: Optional[str] = None
    db_initialized: int
    expire_time: Optional[datetime] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TenantListOut(BaseModel):
    """租户列表项输出"""
    id: int
    tenant_code: str
    tenant_name: str
    short_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    status: int
    db_initialized: int
    expire_time: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
