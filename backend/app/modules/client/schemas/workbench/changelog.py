"""
客户端工作台 - 产品版本升级说明 Schemas
"""

from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class ChangelogItem(BaseModel):
    """展示给租户端的版本升级说明"""
    id: int
    version: str
    title: str
    content: Optional[str] = None
    release_date: date
    is_popup: int

    model_config = {"from_attributes": True}


class ChangelogListOut(BaseModel):
    """版本升级说明分页列表"""
    list: List[ChangelogItem] = []
    total: int = 0
    page: int = 1
    limit: int = 20


class ChangelogPopupOut(BaseModel):
    """待强制弹框的版本升级说明"""
    items: List[ChangelogItem] = []


class ChangelogReadIn(BaseModel):
    """标记已读入参"""
    changelog_ids: List[int] = []
