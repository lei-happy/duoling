"""
意见反馈 Schemas（Console）
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FeedbackHandleIn(BaseModel):
    """处理反馈"""
    status: int = Field(..., ge=0, le=3, description="处理状态")
    reply: Optional[str] = Field(None, max_length=2000, description="回复内容")


class FeedbackOut(BaseModel):
    """反馈详情/列表项"""
    id: int
    tenant_code: Optional[str] = None
    tenant_name: Optional[str] = None
    user_id: int
    user_name: Optional[str] = None
    contact_phone: Optional[str] = None
    title: str
    content: str
    feedback_type: int
    status: int
    reply: Optional[str] = None
    images: List[str] = []
    handler_id: Optional[int] = None
    handler_name: Optional[str] = None
    replied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
