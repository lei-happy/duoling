"""提示词模板 Schema（Console 端）"""

from typing import Optional
from pydantic import BaseModel, Field


class PromptTemplateCreate(BaseModel):
    code: str = Field(..., description="模板编码（全局唯一）")
    name: str
    scene: str = Field("role", description="system/role/scenario")
    content: str
    description: Optional[str] = None


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    scene: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class PromptTemplateOut(BaseModel):
    id: int
    code: str
    name: str
    scene: str
    content: str
    description: Optional[str] = None
    version: int = 1
    status: int = 1
