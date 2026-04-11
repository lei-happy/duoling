"""
系统配置 Schemas
"""

from typing import Optional
from pydantic import BaseModel


class SystemConfigUpdate(BaseModel):
    configValue: str


class SystemConfigOut(BaseModel):
    id: int
    configKey: str
    configValue: Optional[str] = None
    configGroup: Optional[str] = None
    description: Optional[str] = None
    valueType: str
    defaultValue: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "SystemConfigOut":
        return cls(
            id=m.id,
            configKey=m.config_key,
            configValue=m.config_value,
            configGroup=m.config_group,
            description=m.description,
            valueType=m.value_type,
            defaultValue=m.default_value,
        )
