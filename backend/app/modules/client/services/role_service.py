"""
企业端角色管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.biz_role import BizRole
from app.modules.client.models.biz_role_menu import BizRoleMenu
from app.modules.client.schemas.role import (
    BizRoleCreate, BizRoleUpdate, BizRoleOut,
)


class BizRoleService:

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
            sort_order=data.sortOrder,
            remark=data.remark,
        )
        db.add(role)
        await db.flush()
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

        field_map = {
            "roleName": "role_name",
            "sortOrder": "sort_order",
            "status": "status",
            "remark": "remark",
        }
        for sf, mf in field_map.items():
            val = getattr(data, sf, None)
            if val is not None:
                setattr(role, mf, val)

        await db.flush()
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

        # 软删除旧关联
        old = await db.execute(
            select(BizRoleMenu).where(
                BizRoleMenu.role_id == role_id,
                BizRoleMenu.is_deleted == 0,
            )
        )
        for rm in old.scalars().all():
            rm.is_deleted = 1

        # 创建新关联
        for mid in menu_ids:
            db.add(BizRoleMenu(role_id=role_id, menu_id=mid))
        await db.flush()
