"""
产品功能清单 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

_camel_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
)


class ProductFeatureCreate(BaseModel):
    model_config = _camel_config

    feature_code: str
    feature_name: str
    module: Optional[str] = None
    description: Optional[str] = None
    required_tables: Optional[list] = None
    sort_order: int = 0


class ProductFeatureUpdate(BaseModel):
    model_config = _camel_config

    feature_name: Optional[str] = None
    module: Optional[str] = None
    description: Optional[str] = None
    required_tables: Optional[list] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


class AssignedVersion(BaseModel):
    """功能已关联的版本简要信息"""
    model_config = _camel_config

    id: int
    code: str
    name: str


class ProductFeatureOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

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
    assigned_versions: List[AssignedVersion] = []


class VersionFeatureAssign(BaseModel):
    """批量分配功能到版本"""
    model_config = _camel_config

    version_id: int
    feature_ids: List[int]


class VersionFeatureOut(BaseModel):
    model_config = _camel_config

    id: int
    version_id: int
    feature_id: int
    status: int
    feature_code: Optional[str] = None
    feature_name: Optional[str] = None
    module: Optional[str] = None
