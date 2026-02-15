"""
角色管理 Schemas
字段名对齐前端 EleAdminPlus Role 接口（camelCase）
"""

from typing import Optional, List
from pydantic import BaseModel


class RoleOut(BaseModel):
    """角色输出"""
    roleId: int
    roleCode: str
    roleName: str
    roleType: int = 0
    sortNumber: int = 0
    status: int = 1
    comments: Optional[str] = None
    createTime: Optional[str] = None


class RoleCreate(BaseModel):
    """新增角色"""
    roleCode: str
    roleName: str
    roleType: int = 0
    sortNumber: int = 0
    status: int = 1
    comments: Optional[str] = None


class RoleUpdate(BaseModel):
    """修改角色"""
    roleId: int
    roleCode: Optional[str] = None
    roleName: Optional[str] = None
    roleType: Optional[int] = None
    sortNumber: Optional[int] = None
    status: Optional[int] = None
    comments: Optional[str] = None


class RoleMenuUpdate(BaseModel):
    """修改角色菜单"""
    menuIds: List[int] = []
