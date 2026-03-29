"""
角色管理服务
"""

from typing import Optional, List

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.system.role import Role
from app.modules.console.models.system.permission import RoleMenu
from app.modules.console.schemas.system.role import RoleOut, RoleCreate, RoleUpdate


class RoleService:
    """角色管理服务"""

    @staticmethod
    def _to_out(r: Role) -> RoleOut:
        """将 ORM 模型转换为输出"""
        return RoleOut(
            roleId=r.id,
            roleCode=r.role_code,
            roleName=r.role_name,
            roleType=r.role_type,
            sortNumber=r.sort_order,
            status=r.status,
            comments=r.remark,
            createTime=r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
        )

    @staticmethod
    async def page_roles(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        roleName: Optional[str] = None,
        roleCode: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> dict:
        """分页查询角色"""
        query = select(Role).where(Role.is_deleted == 0, Role.role_type == 0)
        if roleName:
            query = query.where(Role.role_name.contains(roleName))
        if roleCode:
            query = query.where(Role.role_code.contains(roleCode))
        if comments:
            query = query.where(Role.remark.contains(comments))

        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        query = query.order_by(Role.sort_order, Role.id)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return {
            "list": [RoleService._to_out(r).model_dump() for r in items],
            "count": count,
        }

    @staticmethod
    async def list_roles(
        db: AsyncSession,
    ) -> List[RoleOut]:
        """查询角色列表（不分页）"""
        query = (
            select(Role)
            .where(Role.is_deleted == 0, Role.role_type == 0)
            .order_by(Role.sort_order, Role.id)
        )
        result = await db.execute(query)
        items = result.scalars().all()
        return [RoleService._to_out(r) for r in items]

    @staticmethod
    async def create_role(db: AsyncSession, data: RoleCreate) -> None:
        """新增角色"""
        # 检查角色编码唯一性
        existing = await db.execute(
            select(Role).where(Role.role_code == data.roleCode, Role.is_deleted == 0)
        )
        if existing.scalar_one_or_none():
            raise BizException("角色编码已存在")

        role = Role(
            role_code=data.roleCode,
            role_name=data.roleName,
            role_type=data.roleType,
            sort_order=data.sortNumber,
            status=data.status,
            remark=data.comments,
        )
        db.add(role)
        await db.flush()

    @staticmethod
    async def update_role(db: AsyncSession, data: RoleUpdate) -> None:
        """修改角色"""
        result = await db.execute(
            select(Role).where(Role.id == data.roleId, Role.is_deleted == 0)
        )
        role = result.scalar_one_or_none()
        if not role:
            raise BizException("角色不存在")

        if data.roleCode is not None:
            # 检查角色编码唯一性
            dup = await db.execute(
                select(Role).where(
                    Role.role_code == data.roleCode,
                    Role.id != data.roleId,
                    Role.is_deleted == 0,
                )
            )
            if dup.scalar_one_or_none():
                raise BizException("角色编码已存在")
            role.role_code = data.roleCode
        if data.roleName is not None:
            role.role_name = data.roleName
        if data.roleType is not None:
            role.role_type = data.roleType
        if data.sortNumber is not None:
            role.sort_order = data.sortNumber
        if data.status is not None:
            role.status = data.status
        if data.comments is not None:
            role.remark = data.comments

        await db.flush()

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int) -> None:
        """删除角色（软删除）"""
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == 0)
        )
        role = result.scalar_one_or_none()
        if not role:
            raise BizException("角色不存在")
        role.is_deleted = 1
        await db.flush()

    @staticmethod
    async def batch_delete(db: AsyncSession, role_ids: List[int]) -> None:
        """批量删除角色（软删除）"""
        result = await db.execute(
            select(Role).where(Role.id.in_(role_ids), Role.is_deleted == 0)
        )
        roles = result.scalars().all()
        for r in roles:
            r.is_deleted = 1
        await db.flush()

    @staticmethod
    async def get_role_menus(db: AsyncSession, role_id: int) -> List[int]:
        """获取角色已分配的菜单 ID 列表"""
        result = await db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
        )
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def update_role_menus(
        db: AsyncSession, role_id: int, menu_ids: List[int]
    ) -> None:
        """修改角色菜单分配"""
        # 验证角色存在
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == 0)
        )
        if not result.scalar_one_or_none():
            raise BizException("角色不存在")

        # 删除旧关联
        await db.execute(
            delete(RoleMenu).where(RoleMenu.role_id == role_id)
        )
        # 新增关联
        for menu_id in menu_ids:
            db.add(RoleMenu(role_id=role_id, menu_id=menu_id))
        await db.flush()
