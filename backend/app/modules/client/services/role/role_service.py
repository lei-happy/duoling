"""
企业端角色管理服务（租户库）
"""

import secrets
from typing import Optional, List, Dict

from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import ROLE_PERSONA_VALUES, normalize_role_personas
from app.common.exceptions import BizException
from app.modules.client.models.role.biz_role import BizRole
from app.modules.client.models.role.biz_role_menu import BizRoleMenu
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.user.biz_user_role import BizUserRole
from app.modules.client.schemas.role.role import (
    BizRoleCreate, BizRoleUpdate, BizRoleOut,
)
from app.modules.client.schemas.user.user import BizUserOut

# 与前端表格列 prop 对齐，仅允许白名单字段参与排序
_ROLE_SORT_COLUMNS = {
    "createTime": BizRole.created_at,
    "roleId": BizRole.id,
}


def _parse_personas(value: Optional[List[str]], *, required: bool) -> Optional[List[str]]:
    """校验岗位视图列表。新建至少一项；编辑未传则不改。"""
    if value is None:
        if required:
            raise BizException("请选择岗位视图")
        return None
    if any(not isinstance(item, str) or item not in ROLE_PERSONA_VALUES for item in value):
        raise BizException("请选择有效的岗位视图")
    personas = normalize_role_personas(value)
    if required and not personas:
        raise BizException("请选择岗位视图")
    return personas


def _role_list_order_clauses(sort: Optional[str], order: Optional[str]):
    """解析分页排序，非法或未传时按 id 降序（与历史默认一致）。"""
    col = _ROLE_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [desc(BizRole.id)]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    if col is BizRole.created_at:
        return [primary, desc(BizRole.id)]
    return [primary]


class BizRoleService:

    @staticmethod
    async def _load_role_stats(
        db: AsyncSession, role_ids: List[int]
    ) -> Dict[int, Dict[str, int]]:
        """批量聚合角色关联用户数、已授权菜单数。"""
        if not role_ids:
            return {}
        stats: Dict[int, Dict[str, int]] = {
            rid: {"userCount": 0, "menuCount": 0} for rid in role_ids
        }

        # 与 list_role_users 一致：只计未删除用户，且按 user_id 去重
        user_rows = await db.execute(
            select(
                BizUserRole.role_id,
                func.count(func.distinct(BizUserRole.user_id)),
            )
            .join(
                BizUser,
                (BizUser.id == BizUserRole.user_id) & (BizUser.is_deleted == 0),
            )
            .where(
                BizUserRole.role_id.in_(role_ids),
                BizUserRole.is_deleted == 0,
            )
            .group_by(BizUserRole.role_id)
        )
        for role_id, cnt in user_rows.all():
            stats[int(role_id)]["userCount"] = int(cnt)

        menu_rows = await db.execute(
            select(BizRoleMenu.role_id, func.count())
            .where(
                BizRoleMenu.role_id.in_(role_ids),
                BizRoleMenu.is_deleted == 0,
            )
            .group_by(BizRoleMenu.role_id)
        )
        for role_id, cnt in menu_rows.all():
            stats[int(role_id)]["menuCount"] = int(cnt)

        return stats

    @staticmethod
    def _roles_to_out(
        roles: List[BizRole], stats: Dict[int, Dict[str, int]]
    ) -> List[BizRoleOut]:
        items: List[BizRoleOut] = []
        for r in roles:
            s = stats.get(r.id) or {}
            items.append(
                BizRoleOut.from_model(
                    r,
                    user_count=s.get("userCount", 0),
                    menu_count=s.get("menuCount", 0),
                )
            )
        return items

    @staticmethod
    async def page_roles(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        role_name: Optional[str] = None,
        role_code: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
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
            base.order_by(*_role_list_order_clauses(sort, order))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        roles = list(result.scalars().all())
        stats = await BizRoleService._load_role_stats(
            db, [r.id for r in roles]
        )
        items = BizRoleService._roles_to_out(roles, stats)

        return {
            "list": [item.model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def list_roles(
        db: AsyncSession,
        role_name: Optional[str] = None,
        role_code: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[BizRoleOut]:
        base = select(BizRole).where(BizRole.is_deleted == 0)
        if role_name:
            base = base.where(BizRole.role_name.contains(role_name))
        if role_code:
            base = base.where(BizRole.role_code.contains(role_code))

        result = await db.execute(
            base.order_by(*_role_list_order_clauses(sort, order))
        )
        roles = list(result.scalars().all())
        stats = await BizRoleService._load_role_stats(
            db, [r.id for r in roles]
        )
        return BizRoleService._roles_to_out(roles, stats)

    @staticmethod
    async def _generate_role_code(db: AsyncSession) -> str:
        """生成角色标识：R + 8 位十六进制，冲突则重试。"""
        for _ in range(12):
            code = "R" + secrets.token_hex(4).upper()
            existing = await db.execute(
                select(BizRole.id).where(
                    BizRole.role_code == code,
                    BizRole.is_deleted == 0,
                )
            )
            if existing.scalar_one_or_none() is None:
                return code
        raise BizException("角色标识生成失败，请稍后重试")

    @staticmethod
    async def create_role(db: AsyncSession, data: BizRoleCreate) -> BizRole:
        role_code = (data.roleCode or "").strip() or None
        if role_code:
            existing = await db.execute(
                select(BizRole).where(
                    BizRole.role_code == role_code,
                    BizRole.is_deleted == 0,
                )
            )
            if existing.scalar_one_or_none():
                raise BizException(f"角色编码 {role_code} 已存在")
        else:
            role_code = await BizRoleService._generate_role_code(db)

        role = BizRole(
            role_code=role_code,
            role_name=data.roleName,
            personas=_parse_personas(data.personas, required=True),
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
        if data.personas is not None:
            role.personas = _parse_personas(data.personas, required=False)

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
    async def list_role_users(db: AsyncSession, role_id: int) -> List[dict]:
        """查询拥有指定角色的员工列表。"""
        role = (
            await db.execute(
                select(BizRole).where(
                    BizRole.id == role_id,
                    BizRole.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not role:
            raise BizException("角色不存在")

        result = await db.execute(
            select(BizUser)
            .join(
                BizUserRole,
                (BizUserRole.user_id == BizUser.id)
                & (BizUserRole.role_id == role_id)
                & (BizUserRole.is_deleted == 0),
            )
            .where(BizUser.is_deleted == 0)
            .order_by(desc(BizUser.id))
        )
        users = list(result.scalars().all())

        # 延迟导入，避免与 user_service 循环依赖
        from app.modules.client.services.user.user_service import BizUserService

        items: List[dict] = []
        for u in users:
            dept_name = await BizUserService._get_dept_name(db, u.department_id)
            items.append(
                BizUserOut.from_model(u, dept_name=dept_name).model_dump()
            )
        return items

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
