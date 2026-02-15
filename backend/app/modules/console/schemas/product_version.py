"""
产品版本 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProductVersionCreate(BaseModel):
    """创建产品版本"""
    version_code: str
    version_name: str
    description: Optional[str] = None
    features: Optional[dict] = None
    max_users: int = 10
    max_vehicles: int = 50
    price: Optional[str] = None
    sort_order: int = 0


class ProductVersionUpdate(BaseModel):
    """更新产品版本"""
    version_name: Optional[str] = None
    description: Optional[str] = None
    features: Optional[dict] = None
    max_users: Optional[int] = None
    max_vehicles: Optional[int] = None
    price: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


class ProductVersionOut(BaseModel):
    """产品版本输出"""
    id: int
    version_code: str
    version_name: str
    description: Optional[str] = None
    features: Optional[dict] = None
    max_users: int
    max_vehicles: int
    price: Optional[str] = None
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
