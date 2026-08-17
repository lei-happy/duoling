"""自有运力推荐引擎协议。

远期智能推荐只替换实现，不改本协议与 API 响应字段。
"""

from __future__ import annotations

from typing import List, Optional, Protocol

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.task import Task


class RecommendReason(BaseModel):
    code: str
    text: str


class RecommendItem(BaseModel):
    capacityId: int
    driverName: str = ""
    driverPhone: str = ""
    plateNumber: str = ""
    trailerPlateNumber: str = ""
    plateCategory: Optional[str] = None
    operationStatus: int = 1
    rank: int = 1
    reasons: List[RecommendReason] = Field(default_factory=list)


class RecommendResult(BaseModel):
    engine: str
    items: List[RecommendItem] = Field(default_factory=list)


class CapacityRecommendEngine(Protocol):
    name: str

    async def recommend(
        self,
        db: AsyncSession,
        task: Task,
        *,
        keyword: Optional[str] = None,
        limit: int = 20,
    ) -> List[RecommendItem]:
        """返回已按推荐顺序排好的运力（rank 由 Service 统一编号）。"""
        ...
