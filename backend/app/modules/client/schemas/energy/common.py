"""能源中心通用 Schemas"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class IdName(BaseModel):
    id: int
    name: str


class PageQuery(BaseModel):
    page: int = 1
    limit: int = 20
    keyword: Optional[str] = None
