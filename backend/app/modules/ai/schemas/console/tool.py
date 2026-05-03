"""工具元数据 Schema（Console 端）"""

from typing import Optional
from pydantic import BaseModel, Field


class ToolOut(BaseModel):
    id: int
    code: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    paramsSchema: Optional[dict] = None
    requiredPermission: Optional[str] = None
    riskLevel: str = "low"
    confirmRequired: bool = False
    isBuiltin: bool = True
    status: int = 1


class ToolStatusUpdate(BaseModel):
    status: int = Field(..., description="0-停用 1-启用")


class ToolSyncResult(BaseModel):
    inserted: int = 0
    updated: int = 0
    orphan: int = 0
