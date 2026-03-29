"""
菜单管理 Schemas
字段名对齐前端 EleAdminPlus Menu 接口（camelCase）
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class MenuOut(BaseModel):
    """菜单输出"""
    menuId: int
    parentId: int = 0
    title: str
    path: Optional[str] = None
    component: Optional[str] = None
    menuType: int = 0
    sortNumber: int = 0
    authority: Optional[str] = None
    icon: Optional[str] = None
    hide: int = 0
    meta: Optional[Any] = None
    createTime: Optional[str] = None
    children: Optional[List["MenuOut"]] = None


class MenuCreate(BaseModel):
    """新增菜单请求"""
    parentId: int = 0
    title: str
    path: Optional[str] = None
    component: Optional[str] = None
    menuType: int = 0
    sortNumber: int = 0
    authority: Optional[str] = None
    icon: Optional[str] = None
    hide: int = 0
    meta: Optional[Any] = None


class MenuUpdate(BaseModel):
    """修改菜单请求"""
    menuId: int
    parentId: Optional[int] = None
    title: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    menuType: Optional[int] = None
    sortNumber: Optional[int] = None
    authority: Optional[str] = None
    icon: Optional[str] = None
    hide: Optional[int] = None
    meta: Optional[Any] = None


class MenuParam(BaseModel):
    """菜单查询参数"""
    title: Optional[str] = None
    path: Optional[str] = None
    authority: Optional[str] = None
    parentId: Optional[int] = None
