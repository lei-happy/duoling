"""
统一响应格式
所有 API 接口返回统一的 JSON 结构
"""

from typing import Any, Optional, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应体"""
    code: int = 0
    message: str = "操作成功"
    data: Optional[T] = None


class PageData(BaseModel, Generic[T]):
    """分页数据"""
    list: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


class PageResponseModel(BaseModel, Generic[T]):
    """分页响应体"""
    code: int = 0
    message: str = "操作成功"
    data: Optional[PageData[T]] = None


def success(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def fail(message: str = "fail", code: int = -1, data: Any = None) -> dict:
    """失败响应"""
    return {"code": code, "message": message, "data": data}
