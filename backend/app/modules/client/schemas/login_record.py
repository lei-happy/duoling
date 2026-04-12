"""
客户端登录日志 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BizLoginLogOut(BaseModel):
    """登录日志输出（与前端表格列 prop 对齐）"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    os: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    ip: Optional[str] = None
    login_type: int = 0
    comments: Optional[str] = None
    createTime: Optional[datetime] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
