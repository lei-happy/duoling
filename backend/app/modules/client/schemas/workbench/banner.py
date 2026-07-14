"""
客户端工作台推广位 Banner Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, field_validator


class BannerItem(BaseModel):
    """展示给客户端的 Banner（不含运营内部字段）"""
    id: int
    image_url: str
    title: str
    link_type: str
    link_url: Optional[str] = None
    open_in_new_tab: int


class BannerListOut(BaseModel):
    items: List[BannerItem] = []


class BannerEventIn(BaseModel):
    """埋点上报入参"""
    banner_id: int
    event_type: str

    @field_validator("event_type")
    @classmethod
    def _check(cls, v: str) -> str:
        if v not in {"view", "click"}:
            raise ValueError("event_type 仅支持 view/click")
        return v
