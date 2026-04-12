"""
企业端数据字典 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class BizDictCreate(BaseModel):
    dictCode: str
    dictName: str
    sortOrder: int = 0
    remark: Optional[str] = None


class BizDictUpdate(BaseModel):
    dictName: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class BizDictOut(BaseModel):
    id: int
    dictCode: str
    dictName: str
    sortOrder: int
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "BizDictOut":
        return cls(
            id=m.id,
            dictCode=m.dict_code,
            dictName=m.dict_name,
            sortOrder=m.sort_order,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )


class BizDictItemCreate(BaseModel):
    dictId: int
    dictCode: str
    itemName: str
    itemValue: str
    sortOrder: int = 0
    remark: Optional[str] = None


class BizDictItemUpdate(BaseModel):
    itemName: Optional[str] = None
    itemValue: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class BizDictItemOut(BaseModel):
    id: int
    dictId: int
    dictCode: str
    itemName: str
    itemValue: str
    sortOrder: int
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "BizDictItemOut":
        return cls(
            id=m.id,
            dictId=m.dict_id,
            dictCode=m.dict_code,
            itemName=m.item_name,
            itemValue=m.item_value,
            sortOrder=m.sort_order,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )


class BizDictItemApiCreate(BaseModel):
    """POST /dictionary-data 请求体（与前端表单字段一致）"""

    dictId: int
    dictCode: Optional[str] = None
    dictDataName: str
    dictDataCode: Optional[str] = None
    sortNumber: Optional[int] = None
    comments: Optional[str] = None


class BizDictItemApiUpdate(BaseModel):
    """PUT /dictionary-data 请求体"""

    dictDataId: int
    dictDataName: Optional[str] = None
    dictDataCode: Optional[str] = None
    sortNumber: Optional[int] = None
    comments: Optional[str] = None
