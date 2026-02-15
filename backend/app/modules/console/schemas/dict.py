"""
数据字典管理 Schemas
字段名对齐前端 EleAdminPlus Dictionary 接口（camelCase）
"""

from typing import Optional
from pydantic import BaseModel


# ---- 字典 ----

class DictOut(BaseModel):
    """字典输出"""
    dictId: int
    dictCode: str
    dictName: str
    sortNumber: int = 0
    comments: Optional[str] = None
    createTime: Optional[str] = None


class DictCreate(BaseModel):
    """新增字典"""
    dictCode: str
    dictName: str
    sortNumber: int = 0
    comments: Optional[str] = None


class DictUpdate(BaseModel):
    """修改字典"""
    dictId: int
    dictCode: Optional[str] = None
    dictName: Optional[str] = None
    sortNumber: Optional[int] = None
    comments: Optional[str] = None


# ---- 字典数据 ----

class DictDataOut(BaseModel):
    """字典数据输出"""
    dictDataId: int
    dictId: int
    dictCode: Optional[str] = None
    dictDataCode: str
    dictDataName: str
    sortNumber: int = 0
    comments: Optional[str] = None
    createTime: Optional[str] = None


class DictDataCreate(BaseModel):
    """新增字典数据"""
    dictId: int
    dictDataCode: str
    dictDataName: str
    sortNumber: int = 0
    comments: Optional[str] = None


class DictDataUpdate(BaseModel):
    """修改字典数据"""
    dictDataId: int
    dictDataCode: Optional[str] = None
    dictDataName: Optional[str] = None
    sortNumber: Optional[int] = None
    comments: Optional[str] = None
