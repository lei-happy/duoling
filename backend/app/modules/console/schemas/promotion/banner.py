"""
推广位 Banner Schemas（Console）
"""

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, field_validator

LINK_TYPES = {"none", "external", "internal"}
TARGET_TYPES = {"all", "version", "tenant"}
STATUSES = {"draft", "published", "offline"}


class BannerBase(BaseModel):
    title: str
    image_url: str
    link_type: str = "none"
    link_url: Optional[str] = None
    open_in_new_tab: int = 1
    target_type: str = "all"
    target_values: Optional[List[str]] = None
    sort_order: int = 0
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    remark: Optional[str] = None

    @field_validator("link_type")
    @classmethod
    def _check_link_type(cls, v: str) -> str:
        if v not in LINK_TYPES:
            raise ValueError(f"link_type 必须是 {LINK_TYPES} 之一")
        return v

    @field_validator("target_type")
    @classmethod
    def _check_target_type(cls, v: str) -> str:
        if v not in TARGET_TYPES:
            raise ValueError(f"target_type 必须是 {TARGET_TYPES} 之一")
        return v

    @field_validator("link_url")
    @classmethod
    def _check_link_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
            raise ValueError("link_url 仅支持 http(s):// 外链或 / 开头的站内路由")
        return v


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_type: Optional[str] = None
    link_url: Optional[str] = None
    open_in_new_tab: Optional[int] = None
    target_type: Optional[str] = None
    target_values: Optional[List[str]] = None
    sort_order: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    remark: Optional[str] = None


class BannerOut(BaseModel):
    id: int
    title: str
    image_url: str
    link_type: str
    link_url: Optional[str] = None
    open_in_new_tab: int
    target_type: str
    target_values: Optional[List[str]] = None
    sort_order: int
    status: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    remark: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BannerStatsSummary(BaseModel):
    """聚合统计概览"""
    view_pv: int = 0
    view_uv: int = 0
    click_pv: int = 0
    click_uv: int = 0
    ctr: float = 0.0  # 点击率 = click_uv / view_uv


class BannerTenantStat(BaseModel):
    """按租户聚合"""
    tenant_code: str
    tenant_name: Optional[str] = None
    view_pv: int = 0
    view_uv: int = 0
    click_pv: int = 0
    click_uv: int = 0


class BannerEventItem(BaseModel):
    """事件明细"""
    id: int
    tenant_code: str
    tenant_name: Optional[str] = None
    user_id: int
    user_phone: Optional[str] = None
    event_type: str
    occurred_at: datetime

    model_config = {"from_attributes": True}
