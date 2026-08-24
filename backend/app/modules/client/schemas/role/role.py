"""
企业端角色管理 Schemas
字段名对齐前端 TypeScript 模型（roleId / roleName / roleCode 等）
"""

from typing import Optional, List
from pydantic import BaseModel

from app.common.enums import normalize_role_personas


class BizRoleCreate(BaseModel):
    model_config = {"extra": "ignore"}

    roleName: str
    comments: Optional[str] = None
    # 可选；不传则由服务端自动生成
    roleCode: Optional[str] = None
    # 小程序岗位视图，新建至少选一个（服务层校验，便于返回口语文案）
    personas: Optional[List[str]] = None


class BizRoleUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    roleId: int
    roleName: Optional[str] = None
    roleCode: Optional[str] = None
    comments: Optional[str] = None
    personas: Optional[List[str]] = None


class BizRoleOut(BaseModel):
    roleId: int
    roleCode: str
    roleName: str
    comments: Optional[str] = None
    personas: List[str] = []
    createTime: Optional[str] = None
    userCount: int = 0
    menuCount: int = 0

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        m,
        user_count: int = 0,
        menu_count: int = 0,
    ) -> "BizRoleOut":
        return cls(
            roleId=m.id,
            roleCode=m.role_code,
            roleName=m.role_name,
            comments=m.remark,
            personas=normalize_role_personas(m.personas),
            createTime=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
            userCount=user_count,
            menuCount=menu_count,
        )


class BizRoleMenuAssign(BaseModel):
    menuIds: List[int]
