"""
产品功能清单 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ProductFeatureCreate(BaseModel):
    feature_code: str
    feature_name: str
    module: Optional[str] = None
    description: Optional[str] = None
    required_tables: Optional[list] = None
    sort_order: int = 0


class ProductFeatureUpdate(BaseModel):
    feature_name: Optional[str] = None
    module: Optional[str] = None
    description: Optional[str] = None
    required_tables: Optional[list] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


class ProductFeatureOut(BaseModel):
    id: int
    feature_code: str
    feature_name: str
    module: Optional[str] = None
    description: Optional[str] = None
    required_tables: Optional[list] = None
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VersionFeatureAssign(BaseModel):
    """批量分配功能到版本"""
    version_id: int
    feature_ids: List[int]


class VersionFeatureOut(BaseModel):
    id: int
    version_id: int
    feature_id: int
    status: int
    feature_code: Optional[str] = None
    feature_name: Optional[str] = None
    module: Optional[str] = None
