"""
工作台「最新动态」Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    occurred_at: datetime
    display_time: str = Field(..., description="当日时分 HH:mm（Asia/Shanghai）")
    summary: str
    event_code: str


class CompanyActivityListOut(BaseModel):
    items: List[CompanyActivityItem]


class CompanyActivityDemoSeedOut(BaseModel):
    inserted: int
