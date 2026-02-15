"""
认证相关 Schemas
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str                       # 手机号或用户名
    password: str
    tenant_code: Optional[str] = None   # 多企业选择时第二步传入


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: "LoginUserInfo"


class LoginUserInfo(BaseModel):
    """登录用户信息"""
    user_id: int
    username: str
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    user_type: int
    tenant_code: Optional[str] = None
    roles: List[str] = []
    force_change_pwd: int = 0


class TenantOption(BaseModel):
    """多企业选择项"""
    tenantCode: str = Field(description="企业编码")
    tenantName: str = Field(description="企业名称")


class MultiTenantResponse(BaseModel):
    """多企业选择响应（需要用户选择进入哪个企业）"""
    needSelectTenant: bool = True
    tenants: List[TenantOption] = []


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    oldPassword: str = Field(description="旧密码")
    newPassword: str = Field(description="新密码", min_length=6)


# ============================================================
# /auth/user-info 接口返回格式
# 字段名对齐前端 EleAdminPlus 期望
# ============================================================

class UserMenuOut(BaseModel):
    """菜单输出（对齐前端 Menu 接口）"""
    menuId: int = Field(description="菜单ID")
    parentId: int = Field(default=0, description="父级ID")
    title: str = Field(description="菜单名称")
    path: Optional[str] = Field(default=None, description="路由路径")
    component: Optional[str] = Field(default=None, description="组件路径")
    menuType: int = Field(default=0, description="类型 0-菜单 1-按钮")
    sortNumber: int = Field(default=0, description="排序号")
    authority: Optional[str] = Field(default=None, description="权限标识")
    icon: Optional[str] = Field(default=None, description="图标")
    hide: int = Field(default=0, description="是否隐藏 0-显示 1-隐藏")
    meta: Optional[Any] = Field(default=None, description="路由元信息")


class UserRoleOut(BaseModel):
    """角色输出（对齐前端 Role 接口）"""
    roleId: int = Field(description="角色ID")
    roleCode: str = Field(description="角色编码")
    roleName: str = Field(description="角色名称")


class UserInfoOut(BaseModel):
    """用户信息输出（/auth/user-info 返回）"""
    userId: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    nickname: Optional[str] = Field(default=None, description="昵称/真实姓名")
    avatar: Optional[str] = Field(default=None, description="头像")
    phone: Optional[str] = Field(default=None, description="手机号")
    email: Optional[str] = Field(default=None, description="邮箱")
    sex: Optional[str] = Field(default=None, description="性别")
    status: Optional[int] = Field(default=None, description="状态")
    themeConfig: Optional[dict] = Field(default=None, description="用户主题配置")
    roles: List[UserRoleOut] = Field(default_factory=list, description="角色列表")
    authorities: List[UserMenuOut] = Field(default_factory=list, description="菜单/权限列表")


class UpdateThemeConfigRequest(BaseModel):
    """更新主题配置请求"""
    themeConfig: Optional[dict] = Field(default=None, description="用户主题配置（JSON格式）")
