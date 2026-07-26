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
            await DriverAuthService._raise_unknown_phone(
                db, phone, fallback="手机号或密码错误"
            )
            return  # pragma: no cover — _raise_unknown_phone always raises

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
            await DriverAuthService._raise_unknown_phone(
                db, phone.strip(), fallback="账号不存在，请联系企业管理员开通"
            )
            return  # pragma: no cover

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
    async def _raise_unknown_phone(
        db: AsyncSession, phone: str, *, fallback: str
    ) -> None:
        """手机号无可用 sys_user 时的诊断：有驾驶员档案但未开通 / 完全不存在。"""
        from app.modules.console.models.driver.sys_driver import SysDriver

        sd_res = await db.execute(
            select(SysDriver.id)
            .where(SysDriver.phone == phone, SysDriver.is_deleted == 0)
            .limit(1)
        )
        if sd_res.scalar_one_or_none() is not None:
            logger.warning(f"驾驶员登录失败：手机号 {phone} 有档案但未开通登录账号")
            raise AuthException("账号不存在，请联系企业管理员开通")

        logger.warning(f"驾驶员登录失败：手机号 {phone} 不存在")
        raise AuthException(fallback)

    @staticmethod
    async def _load_driver_status(
        user: User, tenant_code: str
    ) -> Optional[int]:
        """读取租户库 biz_driver.status；失败时返回 None。"""
        from app.core.database import db_manager
        from app.modules.client.models.capacity.self_capacity.driver.driver import (
            Driver,
        )

        try:
            async for tenant_db in db_manager.get_tenant_session(tenant_code):
                stmt = select(Driver).where(
                    Driver.user_id == user.id,
                    Driver.is_deleted == 0,
                )
                res = await tenant_db.execute(stmt)
                drv = res.scalar_one_or_none()
                if drv is None and user.phone:
                    stmt = select(Driver).where(
                        Driver.phone == user.phone,
                        Driver.is_deleted == 0,
                    )
                    res = await tenant_db.execute(stmt)
                    drv = res.scalar_one_or_none()
                return int(drv.status) if drv is not None else None
        except Exception as e:
            logger.warning(
                f"诊断驾驶员状态失败 tenant={tenant_code} user={user.id}: {e}"
            )
            return None

    @staticmethod
    async def _diagnose_inactive(
        db: AsyncSession, user: User, inactive_uts: list[UserTenant]
    ) -> str:
        """全部驾驶员关联均停用时，按人事状态拼出可读文案。"""
        messages: list[str] = []
        for ut in inactive_uts:
            t_res = await db.execute(
                select(Tenant).where(
                    Tenant.tenant_code == ut.tenant_code,
                    Tenant.is_deleted == 0,
                )
            )
            tenant = t_res.scalar_one_or_none()
            tenant_name = tenant.tenant_name if tenant else ut.tenant_code

            driver_status = await DriverAuthService._load_driver_status(
                user, ut.tenant_code
            )
            if driver_status == 2:
                messages.append(f"当前账号在{tenant_name}已离职")
            elif driver_status == 0:
                messages.append(f"当前账号在{tenant_name}已被冻结")
            else:
                messages.append(
                    f"当前账号在{tenant_name}暂不可用，请联系企业管理员"
                )

        if len(messages) == 1:
            return messages[0]
        return "您的驾驶员账号已停用，请联系企业管理员"

    @staticmethod
    async def _resolve_tenants_and_login(
        db: AsyncSession, user: User, tenant_code: Optional[str]
    ) -> Union[LoginResponse, MultiTenantResponse]:
        # 含 status=0 的全部驾驶员关联，用于诊断离职/冻结
        all_ut_query = select(UserTenant).where(
            UserTenant.user_id == user.id,
            UserTenant.user_type == DRIVER_USER_TYPE,
            UserTenant.is_deleted == 0,
        )
        if tenant_code:
            all_ut_query = all_ut_query.where(UserTenant.tenant_code == tenant_code)

        all_ut_result = await db.execute(all_ut_query)
        all_user_tenants = list(all_ut_result.scalars().all())

        if not all_user_tenants:
            raise AuthException("账号不存在，请联系企业管理员开通")

        active_uts = [ut for ut in all_user_tenants if int(ut.status or 0) == 1]
        inactive_uts = [ut for ut in all_user_tenants if int(ut.status or 0) != 1]

        active_pairs: list[tuple[UserTenant, Tenant]] = []
        for ut in active_uts:
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
            if inactive_uts:
                msg = await DriverAuthService._diagnose_inactive(
                    db, user, inactive_uts
                )
                raise AuthException(msg)
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
