"""
设计对接模块 Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


PRODUCT_LINES = {"console", "client", "mobile", "lite", "other"}
VALID_PRIORITIES = {0, 1, 2, 3}
VALID_STATUSES = {0, 1, 2, 3, 4, 5, 6}


def _normalize_prototype_path(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip().replace("\\", "/").lstrip("/")
    if not v:
        return None
    if ".." in v.split("/"):
        raise ValueError("原型路径不合法")
    lower = v.lower()
    if not (lower.endswith(".html") or lower.endswith(".htm")):
        raise ValueError("请选择 HTML 原型文件")
    if len(v) > 500:
        raise ValueError("原型路径过长，请检查后重试")
    return v


class DesignModuleCreate(BaseModel):
    """创建设计对接模块"""

    title: str = Field(..., min_length=1, max_length=200)
    product_line: str = "other"
    description: Optional[str] = None
    priority: int = 1
    status: int = 0
    prototype_path: Optional[str] = None
    figma_url: Optional[str] = None
    pm_user_id: Optional[int] = None
    pm_name: Optional[str] = None
    designer_user_id: Optional[int] = None
    designer_name: Optional[str] = None
    developer_user_id: Optional[int] = None
    developer_name: Optional[str] = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("请填写模块名称")
        return v

    @field_validator("product_line")
    @classmethod
    def check_product_line(cls, v: str) -> str:
        v = (v or "other").strip()
        if v not in PRODUCT_LINES:
            raise ValueError("请选择有效的产品端")
        return v

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v not in VALID_PRIORITIES:
            raise ValueError("请选择有效的优先级")
        return v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: int) -> int:
        if v not in VALID_STATUSES:
            raise ValueError("请选择有效的状态")
        return v

    @field_validator("prototype_path")
    @classmethod
    def check_prototype_path(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_prototype_path(v)

    @field_validator("figma_url")
    @classmethod
    def check_figma_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if "figma.com" not in v.lower():
            raise ValueError("请填写有效的 Figma 链接")
        if len(v) > 500:
            raise ValueError("Figma 链接过长，请检查后重试")
        return v


class DesignModuleUpdate(BaseModel):
    """更新设计对接模块"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    product_line: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[int] = None
    prototype_path: Optional[str] = None
    figma_url: Optional[str] = None
    pm_user_id: Optional[int] = None
    pm_name: Optional[str] = None
    designer_user_id: Optional[int] = None
    designer_name: Optional[str] = None
    developer_user_id: Optional[int] = None
    developer_name: Optional[str] = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("请填写模块名称")
        return v

    @field_validator("product_line")
    @classmethod
    def check_product_line(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v not in PRODUCT_LINES:
            raise ValueError("请选择有效的产品端")
        return v

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in VALID_PRIORITIES:
            raise ValueError("请选择有效的优先级")
        return v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError("请选择有效的状态")
        return v

    @field_validator("prototype_path")
    @classmethod
    def check_prototype_path(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_prototype_path(v)

    @field_validator("figma_url")
    @classmethod
    def check_figma_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if "figma.com" not in v.lower():
            raise ValueError("请填写有效的 Figma 链接")
        if len(v) > 500:
            raise ValueError("Figma 链接过长，请检查后重试")
        return v


class DesignModuleStatusUpdate(BaseModel):
    """更新状态"""

    status: int

    @field_validator("status")
    @classmethod
    def check_status(cls, v: int) -> int:
        if v not in VALID_STATUSES:
            raise ValueError("请选择有效的状态")
        return v


class DesignModulePriorityUpdate(BaseModel):
    """更新优先级"""

    priority: int

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v not in VALID_PRIORITIES:
            raise ValueError("请选择有效的优先级")
        return v


class DesignModuleSortItem(BaseModel):
    """排序项"""

    id: int
    sort_order: int
    status: Optional[int] = None


class DesignModuleSortRequest(BaseModel):
    """批量排序"""

    items: List[DesignModuleSortItem] = Field(..., min_length=1)


class DesignModuleOut(BaseModel):
    """设计对接模块输出"""

    id: int
    title: str
    product_line: str
    description: Optional[str] = None
    priority: int
    status: int
    prototype_path: Optional[str] = None
    figma_url: Optional[str] = None
    pm_user_id: Optional[int] = None
    pm_name: Optional[str] = None
    designer_user_id: Optional[int] = None
    designer_name: Optional[str] = None
    developer_user_id: Optional[int] = None
    developer_name: Optional[str] = None
    sort_order: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
