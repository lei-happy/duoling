"""
驾驶员登录与企业切换服务

复用 ``console.AuthService`` 的核心逻辑，但在企业列表过滤上强制
``sys_user_tenant.user_type=3``，确保驾驶员 H5 / APP 不会进入到管理员/操作员账号。
"""

from datetime import datetime
from typing import List, Optional, Union

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AuthException
from app.common.utils import verify_password
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.schemas.auth.auth import (
    LoginRequest,
    LoginResponse,
    MultiTenantResponse,
    SwitchTenantRequest,
    TenantOption,
)
from app.modules.console.services.auth.auth_service import AuthService

DRIVER_USER_TYPE = 3


class DriverAuthService:
    """驾驶员端登录 / 切换企业 / 拉取关联企业列表"""

    # ============================================================
    # 登录（密码）
    # ============================================================

    @staticmethod
    async def driver_login(
        db: AsyncSession, request: LoginRequest
    ) -> Union[LoginResponse, MultiTenantResponse]:
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
            logger.warning(f"驾驶员登录失败：手机号 {phone} 不存在")
            raise AuthException("手机号或密码错误")

        if not verify_password(request.password, user.password):
            logger.warning(f"驾驶员登录失败：用户 {phone}(id={user.id}) 密码校验不通过")
            raise AuthException("手机号或密码错误")

        return await DriverAuthService._resolve_tenants_and_login(
            db, user, request.tenant_code
        )

    # ============================================================
    # 登录（验证码）
    # ============================================================

    @staticmethod
    async def driver_sms_login(
        db: AsyncSession,
        phone: str,
        code: str,
        tenant_code: Optional[str] = None,
    ) -> Union[LoginResponse, MultiTenantResponse]:
        from app.modules.open.services.sms_service import PURPOSE_LOGIN, SmsService

        # 预校验（不消费）
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

        resp = await DriverAuthService._resolve_tenants_and_login(
            db, user, tenant_code
        )

        # 真正命中租户时消费验证码
        if isinstance(resp, LoginResponse):
            await SmsService.verify_code(db, phone, code, PURPOSE_LOGIN)

        return resp

    # ============================================================
    # 共用：根据用户找到 user_type=3 的关联企业列表，单一则直接登录，多则返回选择
    # ============================================================

    @staticmethod
    async def _resolve_tenants_and_login(
        db: AsyncSession, user: User, tenant_code: Optional[str]
    ) -> Union[LoginResponse, MultiTenantResponse]:
        ut_query = select(UserTenant).where(
            UserTenant.user_id == user.id,
            UserTenant.user_type == DRIVER_USER_TYPE,  # 强制 user_type=3
            UserTenant.status == 1,
            UserTenant.is_deleted == 0,
        )
        if tenant_code:
            ut_query = ut_query.where(UserTenant.tenant_code == tenant_code)

        ut_result = await db.execute(ut_query)
        user_tenants = list(ut_result.scalars().all())
        if not user_tenants:
            raise AuthException("您还未被任何企业开通为驾驶员，请联系企业管理员")

        active_pairs: list[tuple[UserTenant, Tenant]] = []
        for ut in user_tenants:
            t_res = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_code == ut.tenant_code,
                    Tenant.is_deleted == 0,
                )
            )
            tenant = t_res.scalar_one_or_none()
            if not tenant or tenant.status != 1:
                continue
            if tenant.expire_time and tenant.expire_time < datetime.now():
                continue
            active_pairs.append((ut, tenant))

        if not active_pairs:
            raise AuthException("您所属的企业暂未开通或已过期，请联系企业管理员")

        if len(active_pairs) == 1:
            ut, tenant = active_pairs[0]
            return await AuthService._build_login_response(
                db, user, tenant.tenant_code, ut.user_type
            )

        if not tenant_code:
            tenants = [
                TenantOption(
                    tenantCode=t.tenant_code,
                    tenantName=t.tenant_name,
                )
                for _, t in active_pairs
            ]
            return MultiTenantResponse(tenants=tenants)

        # tenant_code 已指定但匹配多于一条（异常）→ 取首条
        ut, tenant = active_pairs[0]
        return await AuthService._build_login_response(
            db, user, tenant.tenant_code, ut.user_type
        )

    # ============================================================
    # 已登录后：可见企业列表（仅 user_type=3）
    # ============================================================

    @staticmethod
    async def list_driver_tenants(
        db: AsyncSession, user_id: int
    ) -> List[TenantOption]:
        ut_res = await db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user_id,
                UserTenant.user_type == DRIVER_USER_TYPE,
                UserTenant.status == 1,
                UserTenant.is_deleted == 0,
            )
        )
        user_tenants = list(ut_res.scalars().all())

        items: List[TenantOption] = []
        for ut in user_tenants:
            t_res = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_code == ut.tenant_code,
                    Tenant.is_deleted == 0,
                    Tenant.status == 1,
                )
            )
            tenant = t_res.scalar_one_or_none()
            if not tenant:
                continue
            if tenant.expire_time and tenant.expire_time < datetime.now():
                continue
            items.append(
                TenantOption(
                    tenantCode=tenant.tenant_code,
                    tenantName=tenant.tenant_name,
                )
            )
        return items

    # ============================================================
    # 切换企业（已登录）
    # ============================================================

    @staticmethod
    async def switch_tenant(
        db: AsyncSession, user_id: int, request: SwitchTenantRequest
    ) -> LoginResponse:
        u_res = await db.execute(
            select(User).where(
                User.id == user_id, User.is_deleted == 0, User.status == 1
            )
        )
        user = u_res.scalar_one_or_none()
        if not user:
            raise AuthException("用户不存在或已停用")

        ut_res = await db.execute(
            select(UserTenant).where(
                UserTenant.user_id == user_id,
                UserTenant.tenant_code == request.tenant_code,
                UserTenant.user_type == DRIVER_USER_TYPE,
                UserTenant.status == 1,
                UserTenant.is_deleted == 0,
            )
        )
        ut = ut_res.scalar_one_or_none()
        if not ut:
            raise AuthException("您无权访问该企业，或未在该企业被开通为驾驶员")

        t_res = await db.execute(
            select(Tenant).where(
                Tenant.tenant_code == request.tenant_code,
                Tenant.is_deleted == 0,
                Tenant.status == 1,
            )
        )
        tenant = t_res.scalar_one_or_none()
        if not tenant:
            raise AuthException("企业不存在或已停用")

        if tenant.expire_time and tenant.expire_time < datetime.now():
            raise AuthException("企业授权已过期")

        return await AuthService._build_login_response(
            db, user, tenant.tenant_code, ut.user_type
        )
