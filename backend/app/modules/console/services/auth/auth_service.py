"""
认证服务
处理登录、Token签发、用户信息/菜单/权限查询
"""

from datetime import datetime, timedelta
from typing import Optional, List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import get_settings
from app.core.security import TokenData, create_access_token, create_refresh_token, decode_refresh_token
from app.common.utils import verify_password, hash_password
from app.common.exceptions import AuthException
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.console.models.system.user_role import UserRole
from app.modules.console.models.system.role import Role
from app.modules.console.models.system.menu import Menu
from app.modules.console.models.system.permission import RoleMenu
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.tenant.tenant_product import TenantProduct
from app.modules.console.services.product.product_feature_service import ProductFeatureService
from app.modules.console.schemas.auth.auth import (
    LoginRequest, LoginResponse, LoginUserInfo,
    TenantOption, MultiTenantResponse,
    ChangePasswordRequest, RefreshTokenRequest, RefreshTokenResponse,
    UserInfoOut, UserRoleOut, UserMenuOut,
    UpdateProfileRequest, UpdateThemeConfigRequest, SwitchTenantRequest,
)


class AuthService:
    """认证服务"""

    @staticmethod
    async def platform_login(
        db: AsyncSession, request: LoginRequest
    ) -> LoginResponse:
        """
        平台管理后台登录（手机号 + 密码）
        仅允许平台管理员（user_type=0）登录
        """
        result = await db.execute(
            select(User).where(
                User.phone == request.phone,
                User.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"平台登录失败: 手机号 {request.phone} 未找到匹配用户")
            raise AuthException("手机号或密码错误")

        if user.user_type != 0:
            logger.warning(
                f"平台登录失败: 用户 {user.phone}(id={user.id}) user_type={user.user_type}，非平台管理员"
            )
            raise AuthException("无权登录管理后台")

        if user.status != 1:
            logger.warning(
                f"平台登录失败: 用户 {user.phone}(id={user.id}) status={user.status}，账号已停用"
            )
            raise AuthException("账号已被停用")

        if not verify_password(request.password, user.password):
            logger.warning(f"平台登录失败: 用户 {user.phone}(id={user.id}) 密码校验不通过")
            raise AuthException("手机号或密码错误")

        roles = await AuthService._get_user_roles(db, user.id)

        settings = get_settings()
        token_data = TokenData(
            user_id=user.id,
            phone=user.phone,
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
                phone=user.phone,
                real_name=user.real_name,
                avatar=user.avatar,
                user_type=user.user_type,
                tenant_code=None,
                roles=[r.role_code for r in roles],
            ),
        )

    # ============================================================
    # 平台管理后台验证码登录
    # ============================================================

    @staticmethod
    async def platform_sms_login(
        db: AsyncSession, phone: str, code: str
    ) -> LoginResponse:
        """
        平台管理后台验证码登录
        校验验证码 → 查 sys_user (user_type==0) → 签发 JWT
        """
        from app.modules.open.services.sms_service import SmsService, PURPOSE_LOGIN
        await SmsService.verify_code(db, phone, code, PURPOSE_LOGIN)

        result = await db.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("该手机号未注册")

        if user.user_type != 0:
            raise AuthException("无权登录管理后台")

        if user.status != 1:
            raise AuthException("账号已被停用")

        roles = await AuthService._get_user_roles(db, user.id)

        settings = get_settings()
        token_data = TokenData(
            user_id=user.id,
            phone=user.phone,
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
                phone=user.phone,
                real_name=user.real_name,
                avatar=user.avatar,
                user_type=user.user_type,
                tenant_code=None,
                roles=[r.role_code for r in roles],
            ),
        )

    # ============================================================
    # 客户端登录（手机号 + 多企业选择）
    # ============================================================

    @staticmethod
    async def client_login(
        db: AsyncSession, request: LoginRequest
    ) -> Union[LoginResponse, MultiTenantResponse]:
        """
        客户端登录（手机号 + 密码）
        - 通过 sys_user_tenant 查找用户关联的所有企业
        - 多企业时返回选择列表，tenant_code 为第二步传入
        """
        phone = request.phone.strip()

        result = await db.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == 0,
                User.status == 1,
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"客户端登录失败: 手机号 {phone} 未找到匹配用户")
            raise AuthException("手机号或密码错误")

        if not verify_password(request.password, user.password):
            logger.warning(f"客户端登录失败: 用户 {phone}(id={user.id}) 密码校验不通过")
            raise AuthException("手机号或密码错误")

        ut_query = select(UserTenant).where(
            UserTenant.user_id == user.id,
            UserTenant.status == 1,
            UserTenant.is_deleted == 0,
        )
        if request.tenant_code:
            ut_query = ut_query.where(UserTenant.tenant_code == request.tenant_code)

        ut_result = await db.execute(ut_query)
        user_tenants = list(ut_result.scalars().all())

        if not user_tenants:
            raise AuthException("您的企业账号尚未激活或已过期，请联系管理员")

        active_pairs: List[tuple] = []
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
                continue
            if tenant.expire_time and tenant.expire_time < datetime.now():
                tenant.status = 3
                await db.flush()
                continue
            active_pairs.append((ut, tenant))

        if not active_pairs:
            raise AuthException("您的企业账号尚未激活或已过期，请联系管理员")

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

        if active_pairs:
            ut, tenant = active_pairs[0]
            return await AuthService._build_login_response(
                db, user, tenant.tenant_code, ut.user_type
            )

        raise AuthException("手机号或密码错误")

    # ============================================================
    # 客户端验证码登录
    # ============================================================

    @staticmethod
    async def client_sms_login(
        db: AsyncSession, phone: str, code: str,
        tenant_code: Optional[str] = None,
    ) -> Union[LoginResponse, MultiTenantResponse]:
        """
        客户端验证码登录
        校验验证码 → 查 sys_user → 多租户选择 → 签发 JWT
        """
        from app.modules.open.services.sms_service import SmsService, PURPOSE_LOGIN
        await SmsService.verify_code(db, phone, code, PURPOSE_LOGIN, consume=False)

        result = await db.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == 0,
                User.status == 1,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("该手机号未注册")

        ut_query = select(UserTenant).where(
            UserTenant.user_id == user.id,
            UserTenant.status == 1,
            UserTenant.is_deleted == 0,
        )
        if tenant_code:
            ut_query = ut_query.where(UserTenant.tenant_code == tenant_code)

        ut_result = await db.execute(ut_query)
        user_tenants = list(ut_result.scalars().all())

        if not user_tenants:
            raise AuthException("您的企业账号尚未激活或已过期，请联系管理员")

        active_pairs: List[tuple] = []
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
                continue
            if tenant.expire_time and tenant.expire_time < datetime.now():
                tenant.status = 3
                await db.flush()
                continue
            active_pairs.append((ut, tenant))

        if not active_pairs:
            raise AuthException("您的企业账号尚未激活或已过期，请联系管理员")

        if len(active_pairs) == 1:
            ut, tenant = active_pairs[0]
            await SmsService.verify_code(db, phone, code, PURPOSE_LOGIN)
            return await AuthService._build_login_response(
                db, user, tenant.tenant_code, ut.user_type
            )

        if len(active_pairs) > 1 and not tenant_code:
            tenants = [
                TenantOption(
                    tenantCode=t.tenant_code,
                    tenantName=t.tenant_name,
                )
                for _, t in active_pairs
            ]
            return MultiTenantResponse(tenants=tenants)

        if active_pairs:
            ut, tenant = active_pairs[0]
            await SmsService.verify_code(db, phone, code, PURPOSE_LOGIN)
            return await AuthService._build_login_response(
                db, user, tenant.tenant_code, ut.user_type
            )

        raise AuthException("登录失败")

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
            phone=user.phone,
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
                phone=user.phone,
                real_name=user.real_name,
                avatar=user.avatar,
                user_type=user_type,
                tenant_code=tenant_code,
                roles=[r.role_code for r in roles],
                force_change_pwd=user.force_change_pwd,
            ),
        )

    # ============================================================
    # 切换租户
    # ============================================================

    @staticmethod
    async def get_user_tenants(
        db: AsyncSession, user_id: int
    ) -> List[TenantOption]:
        """获取用户关联的所有有效租户列表"""
        ut_result = await db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user_id,
                UserTenant.status == 1,
                UserTenant.is_deleted == 0,
            )
        )
        user_tenants = list(ut_result.scalars().all())

        tenants: List[TenantOption] = []
        for ut in user_tenants:
            tenant_result = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_code == ut.tenant_code,
                    Tenant.is_deleted == 0,
                    Tenant.status == 1,
                )
            )
            tenant = tenant_result.scalar_one_or_none()
            if not tenant:
                continue
            if tenant.expire_time and tenant.expire_time < datetime.now():
                continue
            tenants.append(TenantOption(
                tenantCode=tenant.tenant_code,
                tenantName=tenant.tenant_name,
            ))
        return tenants

    @staticmethod
    async def switch_tenant(
        db: AsyncSession, user_id: int, request: SwitchTenantRequest
    ) -> LoginResponse:
        """切换到目标租户，签发新的 Token"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0, User.status == 1)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在或已停用")

        ut_result = await db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user_id,
                UserTenant.tenant_code == request.tenant_code,
                UserTenant.status == 1,
                UserTenant.is_deleted == 0,
            )
        )
        ut = ut_result.scalar_one_or_none()
        if not ut:
            raise AuthException("您无权访问该企业")

        tenant_result = await db.execute(
            select(Tenant).where(
                Tenant.tenant_code == request.tenant_code,
                Tenant.is_deleted == 0,
                Tenant.status == 1,
            )
        )
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            raise AuthException("企业不存在或已停用")

        if tenant.expire_time and tenant.expire_time < datetime.now():
            raise AuthException("企业授权已过期")

        return await AuthService._build_login_response(
            db, user, tenant.tenant_code, ut.user_type
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

        roles = await AuthService._get_user_roles(
            db, user.id, token_data.tenant_code
        )

        settings = get_settings()
        new_token_data = TokenData(
            user_id=user.id,
            phone=user.phone,
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

        if not verify_password(request.oldPassword, user.password):
            raise AuthException("旧密码错误")

        if request.oldPassword == request.newPassword:
            raise AuthException("新密码不能与旧密码相同")

        user.password = hash_password(request.newPassword)
        user.force_change_pwd = 0
        await db.commit()

        logger.info(f"用户 {user.phone} 已修改密码")

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
            .where(
                UserRole.user_id == user_id,
                UserRole.is_deleted == 0,
                Role.is_deleted == 0,
            )
        )
        if tenant_code is not None:
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
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在")

        roles = await AuthService._get_user_roles(db, user_id, tenant_code)
        role_codes = [r.role_code for r in roles]

        # client 端：先查租户已启用的 feature_codes，菜单裁剪与 user-info.features 共用一次查询
        feature_codes: List[str] = []
        if app_type == "client" and tenant_code:
            try:
                feature_codes = await AuthService._get_tenant_feature_codes(
                    db, tenant_code
                )
            except Exception as e:
                logger.exception(
                    f"[get_user_info] 获取企业 feature_codes 失败 "
                    f"tenant_code={tenant_code} user_id={user_id} err={e!r}"
                )
                feature_codes = []

        menus = await AuthService._get_user_menus(
            db, user_id, role_codes, app_type,
            tenant_code=tenant_code,
            pre_fetched_features=(
                feature_codes if app_type == "client" and tenant_code else None
            ),
        )

        tenant_name = None
        system_name = None
        user_type = None
        menu_version = None
        if tenant_code:
            tenant_result = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_code == tenant_code,
                    Tenant.is_deleted == 0,
                )
            )
            tenant = tenant_result.scalar_one_or_none()
            if tenant:
                tenant_name = tenant.tenant_name
                system_name = tenant.system_name
                menu_version = tenant.menu_version or 0

            ut_result = await db.execute(
                select(UserTenant.user_type).where(
                    UserTenant.user_id == user_id,
                    UserTenant.tenant_code == tenant_code,
                    UserTenant.is_deleted == 0,
                )
            )
            user_type = ut_result.scalar()

        gender_map = {0: None, 1: "男", 2: "女"}
        return UserInfoOut(
            userId=user.id,
            phone=user.phone,
            nickname=user.real_name,
            avatar=user.avatar,
            email=user.email,
            sex=gender_map.get(user.gender),
            status=user.status,
            themeConfig=user.theme_config,
            tenantName=tenant_name,
            systemName=system_name,
            userType=user_type,
            menuVersion=menu_version,
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
            features=feature_codes,
        )

    @staticmethod
    async def _get_user_menus(
        db: AsyncSession, user_id: int, role_codes: List[str],
        app_type: str = "platform",
        tenant_code: Optional[str] = None,
        pre_fetched_features: Optional[List[str]] = None,
    ) -> List[Menu]:
        """
        获取用户可访问的菜单列表。
        client 端额外根据企业产品版本的功能清单过滤菜单。

        :param pre_fetched_features: 上层已查询过的企业 feature_codes，
            传入后避免在本方法内重复查询；传 None 时按原逻辑现查。
        """
        allowed_feature_codes = None
        if app_type == "client" and tenant_code:
            if pre_fetched_features is not None:
                allowed_feature_codes = pre_fetched_features
            else:
                try:
                    allowed_feature_codes = await AuthService._get_tenant_feature_codes(
                        db, tenant_code
                    )
                except Exception as e:
                    logger.exception(
                        f"[菜单版本裁剪降级] 获取企业版本功能清单失败 "
                        f"tenant_code={tenant_code} user_id={user_id} app_type={app_type} "
                        f"将跳过版本过滤、按角色返回全量菜单 err={e!r}"
                    )
                    allowed_feature_codes = None
            if allowed_feature_codes is not None and not allowed_feature_codes:
                logger.warning(
                    f"[菜单版本裁剪降级] 企业 {tenant_code} 当前没有任何有效授权"
                    f" → allowed_feature_codes 为空，将按角色返回不含 feature_code 限制的菜单。"
                    f" 若运营预期看到限制后的菜单，请检查 sys_tenant_product 状态/end_time。"
                )

        is_admin = "super_admin" in role_codes

        if not is_admin and app_type == "client" and tenant_code:
            ut_result = await db.execute(
                select(UserTenant.user_type).where(
                    UserTenant.user_id == user_id,
                    UserTenant.tenant_code == tenant_code,
                    UserTenant.is_deleted == 0,
                )
            )
            ut_type = ut_result.scalar()
            if ut_type == 1:
                is_admin = True

        if is_admin:
            query = (
                select(Menu)
                .where(
                    Menu.app_type == app_type,
                    Menu.status == 1,
                    Menu.is_deleted == 0,
                )
            )
        else:
            query = (
                select(Menu)
                .join(RoleMenu, RoleMenu.menu_id == Menu.id)
                .join(Role, Role.id == RoleMenu.role_id)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(
                    UserRole.user_id == user_id,
                    UserRole.is_deleted == 0,
                    Menu.app_type == app_type,
                    Menu.status == 1,
                    Menu.is_deleted == 0,
                    RoleMenu.is_deleted == 0,
                )
                .distinct()
            )

        if allowed_feature_codes is not None and len(allowed_feature_codes) > 0:
            from sqlalchemy import or_
            query = query.where(
                or_(
                    Menu.feature_code.in_(allowed_feature_codes),
                    Menu.feature_code.is_(None),
                )
            )

        query = query.order_by(Menu.sort_order, Menu.id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def _get_tenant_feature_codes(
        db: AsyncSession, tenant_code: str
    ) -> List[str]:
        """获取企业所有有效版本对应的 feature_code 列表"""
        from sqlalchemy import or_

        now = datetime.now()
        result = await db.execute(
            select(TenantProduct.version_id).where(
                TenantProduct.tenant_code == tenant_code,
                TenantProduct.is_deleted == 0,
                TenantProduct.status == 1,
                or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > now),
            )
        )
        version_ids = list(result.scalars().all())
        if not version_ids:
            return []

        return await ProductFeatureService.get_feature_codes_by_version_ids(
            db, version_ids
        )

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

    # ============================================================
    # 个人资料更新（/auth/user 使用）
    # ============================================================

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: int,
        request: UpdateProfileRequest,
        tenant_db: Optional[AsyncSession] = None,
    ) -> dict:
        """
        更新个人资料，同步更新平台库 sys_user 和租户库 biz_user
        """
        from app.modules.client.models.user.biz_user import BizUser

        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在")

        gender_map = {"男": 1, "女": 2}

        if request.nickname is not None:
            user.real_name = request.nickname
        if request.email is not None:
            user.email = request.email
        if request.avatar is not None:
            user.avatar = request.avatar
        if request.sex is not None:
            user.gender = gender_map.get(request.sex, 0)

        await db.commit()
        await db.refresh(user)

        if tenant_db:
            biz_result = await tenant_db.execute(
                select(BizUser).where(
                    BizUser.phone == user.phone,
                    BizUser.is_deleted == 0,
                )
            )
            biz_user = biz_result.scalar_one_or_none()
            if biz_user:
                if request.nickname is not None:
                    biz_user.nickname = request.nickname
                    biz_user.real_name = request.nickname
                if request.email is not None:
                    biz_user.email = request.email
                if request.avatar is not None:
                    biz_user.avatar = request.avatar
                if request.sex is not None:
                    biz_user.gender = gender_map.get(request.sex, 0)
                await tenant_db.commit()

        gender_reverse = {0: None, 1: "男", 2: "女"}
        return {
            "nickname": user.real_name,
            "email": user.email,
            "avatar": user.avatar,
            "sex": gender_reverse.get(user.gender),
        }
