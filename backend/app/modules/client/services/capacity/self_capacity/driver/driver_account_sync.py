"""
驾驶员登录账号同步（biz_driver -> sys_user / sys_user_tenant）。

企业端在「驾驶员管理」创建/编辑驾驶员时，除了写租户库 biz_driver 及同步
平台摘要 sys_driver 外，还需要让司机能够登录 H5 端。H5 登录强制要求平台库
存在 ``sys_user`` + ``sys_user_tenant(user_type=3)``，且租户库 ``biz_driver.user_id``
回填到对应 sys_user.id。

本服务以手机号（phone）作为关联标识，复用 ``BizPlatformUserSync`` 的底层查找，
但不镜像任何 client 端菜单/角色（驾驶员 H5 无需 client 菜单权限）。

关键边界：
- ``sys_user_tenant`` 的唯一约束是 (user_id, tenant_code)。若该手机号在本企业
  已是员工/管理员（user_type=1/2），则无法再叠加 user_type=3，视为冲突，不覆盖。
- 删除驾驶员仅软删本企业 ``sys_user_tenant``，不删全局 ``sys_user``（可能在其它企业仍有效）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import hash_password
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.services.user.platform_user_sync import BizPlatformUserSync
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant

DRIVER_USER_TYPE = 3
DEFAULT_DRIVER_PASSWORD = "123456"


@dataclass
class AccountSyncResult:
    """账号同步结果，供 API 层决定是否提示冲突。"""

    opened: bool = False
    user_id: Optional[int] = None
    conflict: bool = False
    message: str = ""


def _driver_status_to_active(driver_status: int) -> int:
    """biz_driver.status: 0-冻结 1-在职 2-离职 -> sys_user_tenant.status: 1 仅在职时启用。"""
    return 1 if int(driver_status or 0) == 1 else 0


class DriverPlatformAccountSync:
    """驾驶员登录账号（平台库）同步服务。"""

    @staticmethod
    async def _load_driver(
        tenant_db: AsyncSession, driver_id: int
    ) -> Optional[Driver]:
        r = await tenant_db.execute(
            select(Driver).where(Driver.id == driver_id, Driver.is_deleted == 0)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _backfill_user_id(
        tenant_db: AsyncSession, driver_id: int, user_id: int
    ) -> None:
        await tenant_db.execute(
            update(Driver)
            .where(Driver.id == driver_id)
            .values(user_id=user_id)
        )

    @staticmethod
    async def sync_account(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        driver_id: int,
    ) -> AccountSyncResult:
        """创建/编辑驾驶员后调用：确保 sys_user + sys_user_tenant(3) + 回填 user_id。

        幂等：可重复调用。改手机号时会同步更新已关联 sys_user.phone。
        """
        result = AccountSyncResult()
        driver = await DriverPlatformAccountSync._load_driver(tenant_db, driver_id)
        if driver is None:
            result.message = "驾驶员不存在"
            return result

        phone = (driver.phone or "").strip()
        if not phone:
            result.message = "驾驶员手机号为空，无法开通登录账号"
            return result

        active = _driver_status_to_active(driver.status)

        # 1) 定位平台用户：优先按已回填的 user_id，其次按手机号
        user: Optional[User] = None
        if driver.user_id:
            user = await pdb.get(User, int(driver.user_id))
            if user and user.is_deleted != 0:
                user = None

        if user is not None:
            # 已关联：处理改手机号
            if user.phone != phone:
                dup = await pdb.execute(
                    select(User).where(
                        User.phone == phone,
                        User.is_deleted == 0,
                        User.id != user.id,
                    )
                )
                if dup.scalar_one_or_none():
                    result.conflict = True
                    result.user_id = user.id
                    result.message = f"手机号 {phone} 已被其它平台账号占用，未更新登录账号"
                    return result
                user.phone = phone
            if not user.real_name and driver.name:
                user.real_name = driver.name
            if driver.avatar and not user.avatar:
                user.avatar = driver.avatar
        else:
            user = await BizPlatformUserSync._find_platform_user_by_phone(pdb, phone)
            if user is None:
                user = User(
                    phone=phone,
                    password=hash_password(DEFAULT_DRIVER_PASSWORD),
                    real_name=driver.name,
                    gender=driver.gender or 0,
                    avatar=driver.avatar,
                    user_type=2,  # sys_user 固定占位，实际角色由 user_tenant 决定
                    status=1,
                    force_change_pwd=1,  # 首次登录强制改密
                )
                pdb.add(user)
                await pdb.flush()
            else:
                if not user.real_name and driver.name:
                    user.real_name = driver.name
                if driver.avatar and not user.avatar:
                    user.avatar = driver.avatar

        # 2) upsert sys_user_tenant
        ut_r = await pdb.execute(
            select(UserTenant).where(
                UserTenant.user_id == user.id,
                UserTenant.tenant_code == tenant_code,
            )
        )
        ut = ut_r.scalar_one_or_none()
        if ut is not None:
            if int(ut.user_type) not in (DRIVER_USER_TYPE, 0):
                # 该手机号在本企业已是员工/管理员，唯一约束不允许再叠加驾驶员身份
                result.conflict = True
                result.user_id = user.id
                result.message = (
                    "该手机号已是本企业员工/管理员账号，未重复开通驾驶员登录"
                )
                return result
            ut.user_type = DRIVER_USER_TYPE
            ut.status = active
            ut.is_deleted = 0
        else:
            pdb.add(
                UserTenant(
                    user_id=user.id,
                    tenant_code=tenant_code,
                    user_type=DRIVER_USER_TYPE,
                    status=active,
                )
            )
        await pdb.flush()

        # 3) 回填 biz_driver.user_id
        if driver.user_id != user.id:
            await DriverPlatformAccountSync._backfill_user_id(
                tenant_db, driver_id, user.id
            )

        result.opened = True
        result.user_id = user.id
        return result

    @staticmethod
    async def sync_status(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        driver_id: int,
    ) -> None:
        """人事状态变更后同步 sys_user_tenant.status（冻结/离职 -> 停用登录）。"""
        driver = await DriverPlatformAccountSync._load_driver(tenant_db, driver_id)
        if driver is None or not driver.user_id:
            # 未开通账号则无需处理（也不主动开通，交由 create/update 钩子）
            return
        active = _driver_status_to_active(driver.status)
        await pdb.execute(
            update(UserTenant)
            .where(
                UserTenant.user_id == int(driver.user_id),
                UserTenant.tenant_code == tenant_code,
                UserTenant.user_type == DRIVER_USER_TYPE,
                UserTenant.is_deleted == 0,
            )
            .values(status=active)
        )

    @staticmethod
    async def close_account(
        pdb: AsyncSession,
        tenant_code: str,
        user_id: Optional[int],
        phone: Optional[str],
    ) -> None:
        """删除驾驶员时软删本企业 sys_user_tenant（不删全局 sys_user）。"""
        target_user_id = user_id
        if not target_user_id and phone:
            u = await BizPlatformUserSync._find_platform_user_by_phone(
                pdb, phone.strip()
            )
            target_user_id = u.id if u else None
        if not target_user_id:
            return
        await pdb.execute(
            update(UserTenant)
            .where(
                UserTenant.user_id == int(target_user_id),
                UserTenant.tenant_code == tenant_code,
                UserTenant.user_type == DRIVER_USER_TYPE,
            )
            .values(is_deleted=1, status=0)
        )

    @staticmethod
    async def reset_password(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        driver_id: int,
    ) -> AccountSyncResult:
        """将驾驶员登录密码重置为默认密码并强制下次改密。"""
        result = AccountSyncResult()
        driver = await DriverPlatformAccountSync._load_driver(tenant_db, driver_id)
        if driver is None:
            result.message = "驾驶员不存在"
            return result

        user: Optional[User] = None
        if driver.user_id:
            user = await pdb.get(User, int(driver.user_id))
        if user is None and driver.phone:
            user = await BizPlatformUserSync._find_platform_user_by_phone(
                pdb, driver.phone.strip()
            )
        if user is None:
            result.message = "该驾驶员尚未开通登录账号"
            return result

        user.password = hash_password(DEFAULT_DRIVER_PASSWORD)
        user.force_change_pwd = 1
        await pdb.flush()
        result.opened = True
        result.user_id = user.id
        result.message = f"已重置为默认密码 {DEFAULT_DRIVER_PASSWORD}"
        return result
