"""
客户端操作记录 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BizOperationLogOut(BaseModel):
    """操作日志输出"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    real_name: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None
    ip: Optional[str] = None
    elapsed_time: Optional[int] = None
    status: int = 1
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )
