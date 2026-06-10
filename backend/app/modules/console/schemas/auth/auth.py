"""
认证相关 Schemas
"""

from typing import Optional, List, Any
from pydantic import AliasChoices, BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str                          # 手机号
    password: str
    tenant_code: Optional[str] = None   # 多企业选择时第二步传入


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: "LoginUserInfo"


class LoginUserInfo(BaseModel):
    """登录用户信息"""
    user_id: int
    phone: str
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


class SmsLoginRequest(BaseModel):
    """验证码登录请求"""
    phone: str = Field(description="手机号")
    code: str = Field(description="验证码")
    tenant_code: Optional[str] = Field(default=None, description="企业编码（多企业选择时传入）")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(description="Refresh Token")


class RefreshTokenResponse(BaseModel):
    """刷新 Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """修改密码请求（旧密码校验）；运营端表单字段 password 与 newPassword 等价"""
    oldPassword: str = Field(description="旧密码")
    newPassword: str = Field(
        description="新密码",
        min_length=6,
        validation_alias=AliasChoices("newPassword", "password"),
    )


class SwitchTenantRequest(BaseModel):
    """切换租户请求"""
    tenant_code: str = Field(description="目标租户编码")


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
    phone: str = Field(description="手机号")
    nickname: Optional[str] = Field(default=None, description="昵称/真实姓名")
    avatar: Optional[str] = Field(default=None, description="头像")
    email: Optional[str] = Field(default=None, description="邮箱")
    sex: Optional[str] = Field(default=None, description="性别")
    status: Optional[int] = Field(default=None, description="状态")
    themeConfig: Optional[dict] = Field(default=None, description="用户主题配置")
    workplaceConfig: Optional[dict] = Field(
        default=None, description="工作台个性化配置（快捷操作等）"
    )
    tenantName: Optional[str] = Field(default=None, description="企业名称")
    systemName: Optional[str] = Field(default=None, description="系统自定义名称（客户端左上角显示）")
    organizationId: Optional[int] = Field(
        default=None, description="所属部门ID（client 端，来源 biz_user.department_id）"
    )
    organizationName: Optional[str] = Field(
        default=None, description="所属部门名称（client 端，来源 biz_department.dept_name）"
    )
    userType: Optional[int] = Field(default=None, description="用户类型 1-管理员 2-用户 3-驾驶员")
    menuVersion: Optional[int] = Field(
        default=None,
        description="菜单版本戳：客户端缓存后用于与 /auth/menu-version 比对，若不一致需重新拉取菜单",
    )
    roles: List[UserRoleOut] = Field(default_factory=list, description="角色列表")
    authorities: List[UserMenuOut] = Field(default_factory=list, description="菜单/权限列表")
    features: List[str] = Field(
        default_factory=list,
        description="当前租户已启用的产品功能码（仅 client 端有值）",
    )
    versionCode: Optional[str] = Field(
        default=None,
        description="当前租户生效的产品版本编码（lite/basic/standard/pro/enterprise）",
    )
    versionName: Optional[str] = Field(
        default=None, description="当前租户生效的产品版本名称",
    )


class UpdateProfileRequest(BaseModel):
    """更新个人资料请求（个人中心使用）"""
    nickname: Optional[str] = Field(default=None, description="昵称", max_length=50)
    email: Optional[str] = Field(default=None, description="邮箱", max_length=100)
    avatar: Optional[str] = Field(default=None, description="头像URL", max_length=255)
    sex: Optional[str] = Field(default=None, description="性别（男/女）")


class UpdateThemeConfigRequest(BaseModel):
    """更新主题配置请求"""
    themeConfig: Optional[dict] = Field(default=None, description="用户主题配置（JSON格式）")


class UpdateWorkplaceConfigRequest(BaseModel):
    """更新工作台个性化配置请求"""
    workplaceConfig: Optional[dict] = Field(
        default=None, description="工作台个性化配置（JSON格式）"
    )
