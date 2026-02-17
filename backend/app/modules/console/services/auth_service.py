"""
认证服务
处理登录、Token签发、用户信息/菜单/权限查询
"""

import re
from datetime import datetime, timedelta
from typing import Optional, List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.security import TokenData, create_access_token, create_refresh_token, decode_refresh_token
from app.common.utils import verify_password, hash_password
from app.common.exceptions import AuthException
from app.modules.console.models.user import User
from app.modules.console.models.user_tenant import UserTenant
from app.modules.console.models.user_role import UserRole
from app.modules.console.models.role import Role
from app.modules.console.models.menu import Menu
from app.modules.console.models.permission import RoleMenu
from app.modules.console.models.tenant import Tenant
from app.modules.console.schemas.auth import (
    LoginRequest, LoginResponse, LoginUserInfo,
    TenantOption, MultiTenantResponse,
    ChangePasswordRequest, RefreshTokenRequest, RefreshTokenResponse,
    UserInfoOut, UserRoleOut, UserMenuOut,
    UpdateThemeConfigRequest,
)

# 手机号正则（中国大陆）
_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


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
        refresh_token = create_refresh_token(token_data)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
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

    # ============================================================
    # 客户端登录（手机号/用户名 + 多企业选择）
    # ============================================================

    @staticmethod
    async def client_login(
        db: AsyncSession, request: LoginRequest
    ) -> Union[LoginResponse, MultiTenantResponse]:
        """
        客户端登录
        - username 字段自动检测是手机号还是用户名
        - 通过 sys_user_tenant 查找用户关联的所有企业
        - 多企业时返回选择列表，tenant_code 为第二步传入
        """
        account = request.username.strip()
        is_phone = bool(_PHONE_RE.match(account))

        # Step 1: 查找用户（phone 唯一，最多一条）
        if is_phone:
            query = select(User).where(
                User.phone == account,
                User.is_deleted == 0,
                User.status == 1,
            )
        else:
            query = select(User).where(
                User.username == account,
                User.is_deleted == 0,
                User.status == 1,
            )

        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise AuthException("账号或密码错误")

        # Step 2: 验证密码
        if not verify_password(request.password, user.password):
            raise AuthException("账号或密码错误")

        # Step 3: 通过 sys_user_tenant 查找该用户关联的所有企业
        ut_query = select(UserTenant).where(
            UserTenant.user_id == user.id,
            UserTenant.status == 1,
            UserTenant.is_deleted == 0,
        )
        # 如果指定了 tenant_code（多企业选择第二步），精确过滤
        if request.tenant_code:
            ut_query = ut_query.where(UserTenant.tenant_code == request.tenant_code)

        ut_result = await db.execute(ut_query)
        user_tenants = list(ut_result.scalars().all())

        if not user_tenants:
            raise AuthException("您的企业账号尚未激活或已过期，请联系管理员")

        # Step 4: 逐一检查 sys_tenant 状态，过滤出活跃企业
        active_pairs: List[tuple] = []  # (user_tenant, tenant)
        for ut in user_tenants:
            tenant_result = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_code == ut.tenant_code,
                    Tenant.is_deleted == 0,
                )
            )
            tenant = tenant_result.scalar_one_or_none()
            if not tenant:
                continue
            if tenant.status not in (1,):
                # 0-停用, 2-待审核, 3-已过期 均跳过
                continue
            if tenant.expire_time and tenant.expire_time < datetime.now():
                tenant.status = 3
                await db.flush()
                continue
            active_pairs.append((ut, tenant))

        if not active_pairs:
            raise AuthException("您的企业账号尚未激活或已过期，请联系管理员")

        # Step 5: 根据匹配数量决定返回
        if len(active_pairs) == 1:
            ut, tenant = active_pairs[0]
            return await AuthService._build_login_response(
                db, user, tenant.tenant_code, ut.user_type
            )

        if len(active_pairs) > 1 and not request.tenant_code:
            tenants = [
                TenantOption(
                    tenantCode=t.tenant_code,
                    tenantName=t.tenant_name,
                )
                for _, t in active_pairs
            ]
            return MultiTenantResponse(tenants=tenants)

        # 已指定 tenant_code → 应只剩一个
        if active_pairs:
            ut, tenant = active_pairs[0]
            return await AuthService._build_login_response(
                db, user, tenant.tenant_code, ut.user_type
            )

        raise AuthException("账号或密码错误")

    @staticmethod
    async def _build_login_response(
        db: AsyncSession, user: User, tenant_code: str, user_type: int
    ) -> LoginResponse:
        """
        构造登录成功响应
        :param user_type: 来自 sys_user_tenant.user_type，表示用户在该企业中的角色
        """
        roles = await AuthService._get_user_roles(db, user.id, tenant_code)

        settings = get_settings()
        token_data = TokenData(
            user_id=user.id,
            username=user.username,
            user_type=user_type,
            tenant_code=tenant_code,
            roles=[r.role_code for r in roles],
        )
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=LoginUserInfo(
                user_id=user.id,
                username=user.username,
                real_name=user.real_name,
                avatar=user.avatar,
                user_type=user_type,
                tenant_code=tenant_code,
                roles=[r.role_code for r in roles],
                force_change_pwd=user.force_change_pwd,
            ),
        )

    # ============================================================
    # 刷新 Token
    # ============================================================

    @staticmethod
    async def refresh_token(
        db: AsyncSession, request: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """
        使用 refresh_token 签发新的 access_token + refresh_token
        """
        token_data = decode_refresh_token(request.refresh_token)
        if not token_data:
            raise AuthException("Refresh Token 无效或已过期，请重新登录")

        # 查询用户是否仍然有效
        result = await db.execute(
            select(User).where(
                User.id == token_data.user_id,
                User.is_deleted == 0,
                User.status == 1,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在或已停用，请重新登录")

        # 获取角色
        roles = await AuthService._get_user_roles(
            db, user.id, token_data.tenant_code
        )

        # 签发新的 token 对
        settings = get_settings()
        new_token_data = TokenData(
            user_id=user.id,
            username=user.username,
            user_type=token_data.user_type,
            tenant_code=token_data.tenant_code,
            roles=[r.role_code for r in roles],
        )
        new_access_token = create_access_token(new_token_data)
        new_refresh_token = create_refresh_token(new_token_data)

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    # ============================================================
    # 修改密码
    # ============================================================

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: int, request: ChangePasswordRequest
    ) -> None:
        """
        修改密码
        - 验证旧密码
        - 更新密码（bcrypt hash）
        - 清除 force_change_pwd 标记
        """
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在")

        # 验证旧密码
        if not verify_password(request.oldPassword, user.password):
            raise AuthException("旧密码错误")

        # 新旧密码不能相同
        if request.oldPassword == request.newPassword:
            raise AuthException("新密码不能与旧密码相同")

        # 更新密码
        user.password = hash_password(request.newPassword)
        user.force_change_pwd = 0
        await db.commit()

        logger.info(f"用户 {user.username} 已修改密码")

    @staticmethod
    async def _get_user_roles(
        db: AsyncSession, user_id: int, tenant_code: Optional[str] = None
    ) -> List[Role]:
        """
        获取用户关联的角色列表
        :param tenant_code: 传入时只返回该企业的角色（通过 Role.tenant_code 过滤）
        """
        query = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.is_deleted == 0)
        )
        if tenant_code is not None:
            # 只返回当前企业的租户角色 + 平台公共角色
            query = query.where(
                (Role.tenant_code == tenant_code) | (Role.tenant_code.is_(None))
            )
        result = await db.execute(query)
        return list(result.scalars().all())

    # ============================================================
    # 用户信息 + 菜单 + 权限（/auth/user-info 使用）
    # ============================================================

    @staticmethod
    async def get_user_info(
        db: AsyncSession, user_id: int, app_type: str = "platform",
        tenant_code: Optional[str] = None,
    ) -> UserInfoOut:
        """
        获取完整的用户信息，包括角色和菜单/权限列表
        供 /auth/user-info 接口使用

        :param app_type: "platform" 返回管理后台菜单，"client" 返回客户端菜单
        :param tenant_code: 传入时按企业过滤角色
        """
        # 1. 查询用户
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在")

        # 2. 查询角色（按企业过滤）
        roles = await AuthService._get_user_roles(db, user_id, tenant_code)
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
