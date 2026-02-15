"""
产品更新日志 Schemas
"""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class ChangelogCreate(BaseModel):
    """创建更新记录"""
    version: str
    title: str
    content: Optional[str] = None
    release_date: date
    sort_order: int = 0


class ChangelogUpdate(BaseModel):
    """更新更新记录"""
    version: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    release_date: Optional[date] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


class ChangelogOut(BaseModel):
    """更新记录输出"""
    id: int
    version: str
    title: str
    content: Optional[str] = None
    release_date: date
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
