"""
员工（biz_user）与平台账号（sys_user / sys_user_tenant / sys_user_role）同步。
使客户端登录（仅认平台库）与租户员工管理一致。
同步以手机号（phone）作为关联标识。
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.console.models.system.user_role import UserRole
from app.modules.console.models.system.role import Role
from app.modules.console.models.system.menu import Menu
from app.modules.console.models.system.permission import RoleMenu
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.user.biz_user_role import BizUserRole
from app.modules.client.models.role.biz_role import BizRole


def _biz_to_platform_active(biz_status: int) -> int:
    """biz_user: 0 正常 1 停用 -> sys_user / UserTenant: 1 正常 0 停用"""
    return 1 if biz_status == 0 else 0


def _mirrored_role_code(tenant_code: str, biz_role_code: str) -> str:
    return f"{tenant_code}_{biz_role_code}"


class BizPlatformUserSync:
    """租户员工变更时同步平台侧登录与权限所需数据"""

    @staticmethod
    async def _load_biz_user(
        tenant_db: AsyncSession, biz_user_id: int, *, include_deleted: bool = False
    ) -> Optional[BizUser]:
        q = select(BizUser).where(BizUser.id == biz_user_id)
        if not include_deleted:
            q = q.where(BizUser.is_deleted == 0)
        r = await tenant_db.execute(q)
        return r.scalar_one_or_none()

    @staticmethod
    async def _find_platform_user_by_phone(
        pdb: AsyncSession, phone: str
    ) -> Optional[User]:
        """通过手机号查找平台用户"""
        r = await pdb.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _find_platform_user_for_tenant(
        pdb: AsyncSession, tenant_code: str, phone: str
    ) -> Optional[User]:
        """通过手机号查找在指定租户下的平台用户"""
        r = await pdb.execute(
            select(User)
            .join(UserTenant, UserTenant.user_id == User.id)
            .where(
                User.phone == phone,
                UserTenant.tenant_code == tenant_code,
                User.is_deleted == 0,
                UserTenant.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _ensure_mirrored_platform_role(
        pdb: AsyncSession, tenant_code: str, biz_role: BizRole
    ) -> Role:
        code = _mirrored_role_code(tenant_code, biz_role.role_code)
        r = await pdb.execute(
            select(Role).where(Role.role_code == code, Role.is_deleted == 0)
        )
        existing = r.scalar_one_or_none()
        if existing:
            return existing

        role = Role(
            role_code=code,
            role_name=biz_role.role_name,
            role_type=1,
            tenant_code=tenant_code,
            sort_order=biz_role.sort_order or 0,
            status=1,
        )
        pdb.add(role)
        await pdb.flush()
        await BizPlatformUserSync._seed_client_menus_for_new_role(pdb, role.id)
        return role

    @staticmethod
    async def _seed_client_menus_for_new_role(pdb: AsyncSession, role_id: int) -> None:
        cnt = await pdb.execute(
            select(func.count())
            .select_from(RoleMenu)
            .where(RoleMenu.role_id == role_id, RoleMenu.is_deleted == 0)
        )
        if (cnt.scalar() or 0) > 0:
            return

        mid_rows = await pdb.execute(
            select(Menu.id).where(
                Menu.app_type == "client",
                Menu.is_deleted == 0,
                Menu.status == 1,
            )
        )
        for mid in mid_rows.scalars().all():
            pdb.add(RoleMenu(role_id=role_id, menu_id=mid))

    @staticmethod
    async def _clear_mirrored_user_roles(
        pdb: AsyncSession, platform_user_id: int, tenant_code: str
    ) -> None:
        """移除该用户在本租户下的镜像角色关联（物理删除，避免唯一约束下重复插入）"""
        prefix = f"{tenant_code}_"
        r = await pdb.execute(
            select(Role.id).where(
                Role.tenant_code == tenant_code,
                Role.role_code.startswith(prefix),
                Role.is_deleted == 0,
            )
        )
        role_ids = list(r.scalars().all())
        if not role_ids:
            return
        await pdb.execute(
            delete(UserRole).where(
                UserRole.user_id == platform_user_id,
                UserRole.role_id.in_(role_ids),
            )
        )

    @staticmethod
    async def _sync_user_roles_from_biz(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        platform_user: User,
        biz_user: BizUser,
        role_ids: Sequence[int],
    ) -> None:
        await BizPlatformUserSync._clear_mirrored_user_roles(
            pdb, platform_user.id, tenant_code
        )
        if biz_user.user_type == 1:
            await pdb.flush()
            return

        for rid in role_ids:
            br = await tenant_db.get(BizRole, rid)
            if not br or br.is_deleted != 0:
                continue
            pr = await BizPlatformUserSync._ensure_mirrored_platform_role(
                pdb, tenant_code, br
            )
            pdb.add(UserRole(user_id=platform_user.id, role_id=pr.id))
        await pdb.flush()

    @staticmethod
    async def sync_employee_create(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        biz_user_id: int,
        role_ids: Optional[List[int]],
    ) -> None:
        bu = await BizPlatformUserSync._load_biz_user(tenant_db, biz_user_id)
        if not bu:
            raise BizException("用户不存在")

        rids = list(role_ids or [])

        platform_user = await BizPlatformUserSync._find_platform_user_by_phone(
            pdb, bu.phone
        )

        if platform_user is None:
            platform_user = User(
                phone=bu.phone,
                password=bu.password,
                real_name=bu.real_name or bu.nickname,
                email=bu.email,
                gender=bu.gender,
                user_type=2,
                status=_biz_to_platform_active(bu.status),
                force_change_pwd=0,
            )
            pdb.add(platform_user)
            await pdb.flush()
        else:
            platform_user.password = bu.password
            platform_user.real_name = bu.real_name or bu.nickname
            platform_user.email = bu.email
            platform_user.gender = bu.gender
            platform_user.status = _biz_to_platform_active(bu.status)

        ut_r = await pdb.execute(
            select(UserTenant).where(
                UserTenant.user_id == platform_user.id,
                UserTenant.tenant_code == tenant_code,
            )
        )
        ut = ut_r.scalar_one_or_none()
        if ut:
            ut.user_type = bu.user_type
            ut.status = _biz_to_platform_active(bu.status)
            ut.is_deleted = 0
        else:
            pdb.add(
                UserTenant(
                    user_id=platform_user.id,
                    tenant_code=tenant_code,
                    user_type=bu.user_type,
                    status=_biz_to_platform_active(bu.status),
                )
            )
        await pdb.flush()

        await BizPlatformUserSync._sync_user_roles_from_biz(
            pdb, tenant_db, tenant_code, platform_user, bu, rids
        )

    @staticmethod
    async def sync_employee_update(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        biz_user_id: int,
        role_ids: Optional[List[int]],
    ) -> None:
        bu = await BizPlatformUserSync._load_biz_user(tenant_db, biz_user_id)
        if not bu:
            raise BizException("用户不存在")

        pu = await BizPlatformUserSync._find_platform_user_for_tenant(
            pdb, tenant_code, bu.phone
        )
        if not pu:
            await BizPlatformUserSync.sync_employee_create(
                pdb, tenant_db, tenant_code, biz_user_id, role_ids
            )
            return

        other = await pdb.execute(
            select(User).where(
                User.phone == bu.phone,
                User.is_deleted == 0,
                User.id != pu.id,
            )
        )
        if other.scalar_one_or_none():
            raise BizException("该手机号已被其他平台用户使用")

        pu.real_name = bu.real_name or bu.nickname
        pu.phone = bu.phone
        pu.email = bu.email
        pu.gender = bu.gender
        pu.status = _biz_to_platform_active(bu.status)

        ut_r = await pdb.execute(
            select(UserTenant).where(
                UserTenant.user_id == pu.id,
                UserTenant.tenant_code == tenant_code,
                UserTenant.is_deleted == 0,
            )
        )
        ut = ut_r.scalar_one_or_none()
        if ut:
            ut.user_type = bu.user_type
            ut.status = _biz_to_platform_active(bu.status)
        await pdb.flush()

        if role_ids is not None:
            await BizPlatformUserSync._sync_user_roles_from_biz(
                pdb, tenant_db, tenant_code, pu, bu, role_ids
            )
        else:
            r = await tenant_db.execute(
                select(BizUserRole.role_id).where(
                    BizUserRole.user_id == bu.id,
                    BizUserRole.is_deleted == 0,
                )
            )
            current_rids = [row[0] for row in r.all()]
            await BizPlatformUserSync._sync_user_roles_from_biz(
                pdb, tenant_db, tenant_code, pu, bu, current_rids
            )

    @staticmethod
    async def sync_employee_status(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        biz_user_id: int,
        biz_status: int,
    ) -> None:
        bu = await BizPlatformUserSync._load_biz_user(tenant_db, biz_user_id)
        if not bu:
            raise BizException("用户不存在")
        pu = await BizPlatformUserSync._find_platform_user_for_tenant(
            pdb, tenant_code, bu.phone
        )
        if not pu:
            return
        active = _biz_to_platform_active(biz_status)
        pu.status = active
        ut_r = await pdb.execute(
            select(UserTenant).where(
                UserTenant.user_id == pu.id,
                UserTenant.tenant_code == tenant_code,
                UserTenant.is_deleted == 0,
            )
        )
        ut = ut_r.scalar_one_or_none()
        if ut:
            ut.status = active
        await pdb.flush()

    @staticmethod
    async def sync_employee_remove(
        pdb: AsyncSession,
        tenant_db: AsyncSession,
        tenant_code: str,
        biz_user_id: int,
    ) -> None:
        bu = await BizPlatformUserSync._load_biz_user(
            tenant_db, biz_user_id, include_deleted=True
        )
        if not bu:
            return
        pu = await BizPlatformUserSync._find_platform_user_for_tenant(
            pdb, tenant_code, bu.phone
        )
        if not pu:
            return

        await BizPlatformUserSync._clear_mirrored_user_roles(
            pdb, pu.id, tenant_code
        )

        ut_r = await pdb.execute(
            select(UserTenant).where(
                UserTenant.user_id == pu.id,
                UserTenant.tenant_code == tenant_code,
            )
        )
        ut = ut_r.scalar_one_or_none()
        if ut:
            ut.is_deleted = 1
            ut.status = 0
        await pdb.flush()
