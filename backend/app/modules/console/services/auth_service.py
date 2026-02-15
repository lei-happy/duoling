"""
认证服务
处理登录、Token签发、用户信息/菜单/权限查询
"""

from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.security import TokenData, create_access_token
from app.common.utils import verify_password
from app.common.exceptions import AuthException
from app.modules.console.models.user import User
from app.modules.console.models.user_role import UserRole
from app.modules.console.models.role import Role
from app.modules.console.models.menu import Menu
from app.modules.console.models.permission import RoleMenu
from app.modules.console.models.tenant import Tenant
from app.modules.console.schemas.auth import (
    LoginRequest, LoginResponse, LoginUserInfo,
    UserInfoOut, UserRoleOut, UserMenuOut,
    UpdateThemeConfigRequest,
)


class AuthService:
    """认证服务"""

    @staticmethod
    async def platform_login(
        db: AsyncSession, request: LoginRequest
    ) -> LoginResponse:
        """
        平台管理后台登录
        仅允许平台管理员（user_type=0）登录
        """
        # 查询用户
        result = await db.execute(
            select(User).where(
                User.username == request.username,
                User.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户名或密码错误")

        if user.user_type != 0:
            raise AuthException("无权登录管理后台")

        if user.status != 1:
            raise AuthException("账号已被停用")

        # 验证密码
        if not verify_password(request.password, user.password):
            raise AuthException("用户名或密码错误")

        # 获取角色
        roles = await AuthService._get_user_roles(db, user.id)

        # 签发 Token
        settings = get_settings()
        token_data = TokenData(
            user_id=user.id,
            username=user.username,
            user_type=user.user_type,
            tenant_code=None,
            roles=[r.role_code for r in roles],
        )
        access_token = create_access_token(token_data)

        return LoginResponse(
            access_token=access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=LoginUserInfo(
                user_id=user.id,
                username=user.username,
                real_name=user.real_name,
                avatar=user.avatar,
                user_type=user.user_type,
                tenant_code=None,
                roles=[r.role_code for r in roles],
            ),
        )

    @staticmethod
    async def client_login(
        db: AsyncSession, request: LoginRequest
    ) -> LoginResponse:
        """
        客户端登录
        需要提供 tenant_code，验证租户下的用户
        """
        if not request.tenant_code:
            raise AuthException("请提供企业编码")

        # 检查租户状态
        tenant_result = await db.execute(
            select(Tenant).where(
                Tenant.tenant_code == request.tenant_code,
                Tenant.is_deleted == 0,
            )
        )
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            raise AuthException("企业不存在")
        if tenant.status == 0:
            raise AuthException("企业已被停用，请联系管理员")
        if tenant.status == 2:
            raise AuthException("企业尚未开通，请联系管理员")
        if tenant.status == 3:
            raise AuthException("企业授权已过期，请联系管理员续期")
        if tenant.expire_time and tenant.expire_time < datetime.now():
            # 自动标记为过期
            tenant.status = 3
            await db.flush()
            raise AuthException("企业授权已过期，请联系管理员续期")

        # 查询用户（租户管理员在平台库中）
        result = await db.execute(
            select(User).where(
                User.username == request.username,
                User.tenant_code == request.tenant_code,
                User.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户名或密码错误")

        if user.status != 1:
            raise AuthException("账号已被停用")

        # 验证密码
        if not verify_password(request.password, user.password):
            raise AuthException("用户名或密码错误")

        # 获取角色
        roles = await AuthService._get_user_roles(db, user.id)

        # 签发 Token
        settings = get_settings()
        token_data = TokenData(
            user_id=user.id,
            username=user.username,
            user_type=user.user_type,
            tenant_code=request.tenant_code,
            roles=[r.role_code for r in roles],
        )
        access_token = create_access_token(token_data)

        return LoginResponse(
            access_token=access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=LoginUserInfo(
                user_id=user.id,
                username=user.username,
                real_name=user.real_name,
                avatar=user.avatar,
                user_type=user.user_type,
                tenant_code=request.tenant_code,
                roles=[r.role_code for r in roles],
            ),
        )

    @staticmethod
    async def _get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
        """获取用户关联的角色列表"""
        result = await db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.is_deleted == 0)
        )
        return list(result.scalars().all())

    # ============================================================
    # 用户信息 + 菜单 + 权限（/auth/user-info 使用）
    # ============================================================

    @staticmethod
    async def get_user_info(
        db: AsyncSession, user_id: int, app_type: str = "platform"
    ) -> UserInfoOut:
        """
        获取完整的用户信息，包括角色和菜单/权限列表
        供 /auth/user-info 接口使用

        :param app_type: "platform" 返回管理后台菜单，"client" 返回客户端菜单
        """
        # 1. 查询用户
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在")

        # 2. 查询角色
        roles = await AuthService._get_user_roles(db, user_id)
        role_codes = [r.role_code for r in roles]

        # 3. 查询菜单（根据 app_type 区分平台/客户端）
        menus = await AuthService._get_user_menus(db, user_id, role_codes, app_type)

        # 4. 组装输出（字段名对齐前端 EleAdminPlus）
        gender_map = {0: None, 1: "男", 2: "女"}
        return UserInfoOut(
            userId=user.id,
            username=user.username,
            nickname=user.real_name,
            avatar=user.avatar,
            phone=user.phone,
            email=user.email,
            sex=gender_map.get(user.gender),
            status=user.status,
            themeConfig=user.theme_config,
            roles=[
                UserRoleOut(
                    roleId=r.id,
                    roleCode=r.role_code,
                    roleName=r.role_name,
                )
                for r in roles
            ],
            authorities=[
                UserMenuOut(
                    menuId=m.id,
                    parentId=m.parent_id,
                    title=m.menu_name,
                    path=m.path,
                    component=m.component,
                    menuType=m.menu_type,
                    sortNumber=m.sort_order,
                    authority=m.menu_code,
                    icon=m.icon,
                    hide=0 if m.visible == 1 else 1,
                )
                for m in menus
            ],
        )

    @staticmethod
    async def _get_user_menus(
        db: AsyncSession, user_id: int, role_codes: List[str],
        app_type: str = "platform"
    ) -> List[Menu]:
        """
        获取用户可访问的菜单列表
        - super_admin / tenant_admin 角色返回对应 app_type 的所有菜单
        - 其他角色通过 role_menu 关联查询
        """
        is_admin = (
            "super_admin" in role_codes
            or (app_type == "client" and "tenant_admin" in role_codes)
        )

        if is_admin:
            # 管理员：返回对应 app_type 的所有菜单
            result = await db.execute(
                select(Menu)
                .where(
                    Menu.app_type == app_type,
                    Menu.status == 1,
                    Menu.is_deleted == 0,
                )
                .order_by(Menu.sort_order, Menu.id)
            )
        else:
            # 普通角色：通过 user_role -> role -> role_menu -> menu 查询
            result = await db.execute(
                select(Menu)
                .join(RoleMenu, RoleMenu.menu_id == Menu.id)
                .join(Role, Role.id == RoleMenu.role_id)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(
                    UserRole.user_id == user_id,
                    Menu.app_type == app_type,
                    Menu.status == 1,
                    Menu.is_deleted == 0,
                    RoleMenu.is_deleted == 0,
                )
                .order_by(Menu.sort_order, Menu.id)
                .distinct()
            )
        return list(result.scalars().all())

    # ============================================================
    # 用户主题配置（/auth/user-theme 使用）
    # ============================================================

    @staticmethod
    async def update_theme_config(
        db: AsyncSession, user_id: int, request: UpdateThemeConfigRequest
    ) -> None:
        """
        更新用户主题配置
        """
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在")

        user.theme_config = request.themeConfig
        await db.commit()
