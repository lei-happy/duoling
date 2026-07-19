"""
意见反馈 Schemas（Client）
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class FeedbackCreateIn(BaseModel):
    """提交反馈（title 可选，缺省时由服务端按正文生成列表摘要）"""
    feedback_type: int = Field(..., ge=0, le=3, description="反馈类型")
    title: Optional[str] = Field(None, max_length=200, description="标题（可选）")
    content: str = Field(..., min_length=1, max_length=2000, description="内容")
    images: List[str] = Field(default_factory=list, description="截图URL列表")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        text = v.strip()
        return text or None

    @field_validator("content")
    @classmethod
    def _strip_content(cls, v: str) -> str:
        text = (v or "").strip()
        if not text:
            raise ValueError("不能为空")
        return text

    @field_validator("images")
    @classmethod
    def _check_images(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError("截图最多上传 5 张")
        return v


class FeedbackItemOut(BaseModel):
    """反馈列表/详情"""
    id: int
    tenant_code: Optional[str] = None
    user_id: int
    user_name: Optional[str] = None
    contact_phone: Optional[str] = None
    title: str
    content: str
    feedback_type: int
    status: int
    reply: Optional[str] = None
    images: List[str] = []
    handler_name: Optional[str] = None
    replied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
