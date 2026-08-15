"""
官网线索 Schemas（Console）
"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class WebsiteLeadFollowIn(BaseModel):
    """更新跟进状态"""

    status: int = Field(
        ..., ge=0, le=3, description="0-待联系 1-已联系 2-已转化 3-无效"
    )
    follow_remark: Optional[str] = Field(None, max_length=2000, description="跟进备注")
    converted_tenant_code: Optional[str] = Field(
        None, max_length=32, description="转化后的租户编码"
    )


class WebsiteLeadOut(BaseModel):
    """线索详情 / 列表项"""

    id: int
    company_name: str
    contact_person: str
    contact_phone: str

    fleet_size: Optional[str] = None
    pain_point: Optional[str] = None
    profile_answers: Optional[Dict[str, str]] = None

    stage_band: Optional[str] = None
    stage_name: Optional[str] = None
    total_score: Optional[int] = None
    dim_a: Optional[int] = None
    dim_b: Optional[int] = None
    dim_c: Optional[int] = None
    dim_d: Optional[int] = None

    source_page: Optional[str] = None
    referrer: Optional[str] = None
    client_ip: Optional[str] = None

    status: int
    follow_remark: Optional[str] = None
    handler_id: Optional[int] = None
    handler_name: Optional[str] = None
    contacted_at: Optional[datetime] = None
    converted_tenant_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
