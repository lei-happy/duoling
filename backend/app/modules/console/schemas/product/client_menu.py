"""
客户端菜单管理 Schemas
在 MenuOut 基础上增加 featureCode 字段
"""

from typing import Optional, List, Any
from pydantic import BaseModel


class ClientMenuOut(BaseModel):
    """客户端菜单输出"""
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
    featureCode: Optional[str] = None
    meta: Optional[Any] = None
    createTime: Optional[str] = None
    # 快捷操作配置（sys_menu.quick_action JSON 展开为扁平字段）
    quickActionEnabled: bool = False
    quickActionIcon: Optional[str] = None
    quickActionName: Optional[str] = None
    quickActionColor: Optional[str] = None
    quickActionLink: Optional[str] = None
    quickActionGroup: Optional[str] = None
    quickActionSort: Optional[int] = None
    quickActionDefault: bool = False
    children: Optional[List["ClientMenuOut"]] = None


class ClientMenuCreate(BaseModel):
    """新增客户端菜单"""
    parentId: int = 0
    title: str
    path: Optional[str] = None
    component: Optional[str] = None
    menuType: int = 0
    sortNumber: int = 0
    authority: Optional[str] = None
    icon: Optional[str] = None
    hide: int = 0
    featureCode: Optional[str] = None
    meta: Optional[Any] = None
    # 快捷操作配置
    quickActionEnabled: bool = False
    quickActionIcon: Optional[str] = None
    quickActionName: Optional[str] = None
    quickActionColor: Optional[str] = None
    quickActionLink: Optional[str] = None
    quickActionGroup: Optional[str] = None
    quickActionSort: Optional[int] = None
    quickActionDefault: bool = False


class ClientMenuUpdate(BaseModel):
    """修改客户端菜单"""
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
    featureCode: Optional[str] = None
    meta: Optional[Any] = None
    # 快捷操作配置
    quickActionEnabled: Optional[bool] = None
    quickActionIcon: Optional[str] = None
    quickActionName: Optional[str] = None
    quickActionColor: Optional[str] = None
    quickActionLink: Optional[str] = None
    quickActionGroup: Optional[str] = None
    quickActionSort: Optional[int] = None
    quickActionDefault: Optional[bool] = None
