"""
企业端角色管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.role.biz_role import BizRole
from app.modules.client.models.role.biz_role_menu import BizRoleMenu
from app.modules.client.schemas.role.role import (
    BizRoleCreate, BizRoleUpdate, BizRoleOut,
)


class BizRoleService:

    @staticmethod
    async def page_roles(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        role_name: Optional[str] = None,
        role_code: Optional[str] = None,
    ) -> dict:
        """分页查询角色"""
        base = select(BizRole).where(BizRole.is_deleted == 0)

        if role_name:
            base = base.where(BizRole.role_name.contains(role_name))
        if role_code:
            base = base.where(BizRole.role_code.contains(role_code))

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(BizRole.sort_order, BizRole.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = [BizRoleOut.from_model(r) for r in result.scalars().all()]

        return {
            "list": [item.model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def list_roles(db: AsyncSession) -> List[BizRoleOut]:
        result = await db.execute(
            select(BizRole)
            .where(BizRole.is_deleted == 0)
            .order_by(BizRole.sort_order, BizRole.id)
        )
        return [BizRoleOut.from_model(r) for r in result.scalars().all()]

    @staticmethod
    async def create_role(db: AsyncSession, data: BizRoleCreate) -> BizRole:
        existing = await db.execute(
            select(BizRole).where(
                BizRole.role_code == data.roleCode,
                BizRole.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"角色编码 {data.roleCode} 已存在")

        role = BizRole(
            role_code=data.roleCode,
            role_name=data.roleName,
            sort_order=0,
            remark=data.comments,
        )
        db.add(role)
        await db.flush()
        await db.refresh(role)
        return role

    @staticmethod
    async def update_role(
        db: AsyncSession, role_id: int, data: BizRoleUpdate
    ) -> BizRole:
        result = await db.execute(
            select(BizRole).where(
                BizRole.id == role_id,
                BizRole.is_deleted == 0,
            )
        )
        role = result.scalar_one_or_none()
        if not role:
            raise BizException("角色不存在")

        if data.roleName is not None:
            role.role_name = data.roleName
        if data.comments is not None:
            role.remark = data.comments

        await db.flush()
        await db.refresh(role)
        return role

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int) -> None:
        result = await db.execute(
            select(BizRole).where(
                BizRole.id == role_id,
                BizRole.is_deleted == 0,
            )
        )
        role = result.scalar_one_or_none()
        if not role:
            raise BizException("角色不存在")
        if role.role_code == "admin":
            raise BizException("管理员角色无法删除")
        role.is_deleted = 1
        await db.flush()

    @staticmethod
    async def batch_delete_roles(db: AsyncSession, role_ids: List[int]) -> None:
        for rid in role_ids:
            result = await db.execute(
                select(BizRole).where(
                    BizRole.id == rid,
                    BizRole.is_deleted == 0,
                )
            )
            role = result.scalar_one_or_none()
            if role:
                if role.role_code == "admin":
                    raise BizException(f"管理员角色 {role.role_name} 无法删除")
                role.is_deleted = 1
        await db.flush()

    @staticmethod
    async def get_role_menu_ids(db: AsyncSession, role_id: int) -> List[int]:
        """获取角色已分配的菜单ID列表"""
        result = await db.execute(
            select(BizRoleMenu.menu_id).where(
                BizRoleMenu.role_id == role_id,
                BizRoleMenu.is_deleted == 0,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_role_menus_with_checked(
        tenant_db: AsyncSession,
        platform_db: AsyncSession,
        role_id: int,
        tenant_code: Optional[str] = None,
    ) -> List[dict]:
        """
        获取全部客户端菜单并标记角色已分配的菜单。
        菜单来源：平台库 sys_menu (app_type='client')，按企业版本 feature_code 过滤。
        选中状态：租户库 biz_role_menu。
        """
        from app.modules.console.models.system.menu import Menu as SysMenu
        from sqlalchemy import or_

        checked_ids = set(await BizRoleService.get_role_menu_ids(tenant_db, role_id))

        query = (
            select(SysMenu)
            .where(
                SysMenu.app_type == "client",
                SysMenu.status == 1,
                SysMenu.is_deleted == 0,
            )
        )

        if tenant_code:
            try:
                from app.modules.console.services.auth.auth_service import AuthService
                feature_codes = await AuthService._get_tenant_feature_codes(
                    platform_db, tenant_code
                )
                if feature_codes:
                    query = query.where(
                        or_(
                            SysMenu.feature_code.in_(feature_codes),
                            SysMenu.feature_code.is_(None),
                        )
                    )
            except Exception:
                pass

        query = query.order_by(SysMenu.sort_order, SysMenu.id)
        result = await platform_db.execute(query)
        menus = result.scalars().all()

        return [
            {
                "menuId": m.id,
                "parentId": m.parent_id,
                "title": m.menu_name,
                "path": m.path,
                "component": m.component,
                "menuType": m.menu_type,
                "sortNumber": m.sort_order,
                "authority": m.menu_code,
                "icon": m.icon,
                "hide": 0 if getattr(m, "visible", 1) == 1 else 1,
                "checked": m.id in checked_ids,
            }
            for m in menus
        ]

    @staticmethod
    async def assign_menus(
        db: AsyncSession, role_id: int, menu_ids: List[int]
    ) -> None:
        """分配角色菜单（全量替换）"""
        result = await db.execute(
            select(BizRole).where(
                BizRole.id == role_id,
                BizRole.is_deleted == 0,
            )
        )
        if not result.scalar_one_or_none():
            raise BizException("角色不存在")

        old = await db.execute(
            select(BizRoleMenu).where(
                BizRoleMenu.role_id == role_id,
                BizRoleMenu.is_deleted == 0,
            )
        )
        for rm in old.scalars().all():
            rm.is_deleted = 1

        for mid in menu_ids:
            db.add(BizRoleMenu(role_id=role_id, menu_id=mid))
        await db.flush()
