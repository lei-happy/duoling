"""
运单回单 Schemas

回单 = 运单全量签收后，把签收底单返还货主的人工动作（运单维度，独立于任务）。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WaybillReceiptConfirm(BaseModel):
    """确认回单入参（运单 5 已签收 → 6 已回单）"""

    fileUrls: List[str] = Field(
        default_factory=list, description="回单底单文件 URL 数组（OSS 路径，最多 9 张）",
    )
    fileType: int = Field(1, description="文件类型 1-图片 2-PDF")
    receivedAt: Optional[datetime] = Field(
        default=None, description="回单回收时间，缺省取服务端当前时间",
    )
    remark: Optional[str] = None


class WaybillReceiptOut(BaseModel):
    id: int
    waybillId: int
    fileUrls: List[str] = Field(default_factory=list)
    fileType: int
    receivedAt: datetime
    uploadedBy: Optional[int] = None
    operatorName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "WaybillReceiptOut":
        return cls(
            id=m.id,
            waybillId=m.waybill_id,
            fileUrls=list(m.file_urls or []),
            fileType=int(m.file_type or 1),
            receivedAt=m.received_at,
            uploadedBy=m.uploaded_by,
            operatorName=m.operator_name,
            remark=m.remark,
            createdAt=m.created_at,
        )
