"""
客户端菜单管理服务
操作 sys_menu 表中 app_type='client' 的记录
"""

from typing import Optional, List, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.system.menu import Menu
from app.modules.console.schemas.product.client_menu import (
    ClientMenuCreate, ClientMenuUpdate, ClientMenuOut,
)


class ClientMenuService:

    @staticmethod
    def _build_quick_action(
        enabled: Optional[bool],
        icon: Optional[str],
        name: Optional[str],
        color: Optional[str],
        link: Optional[str],
        group: Optional[str],
        sort: Optional[int],
        default: Optional[bool],
    ) -> Optional[dict]:
        """将扁平字段组装为 quick_action JSON；enabled=False/None 时返回 None"""
        if not enabled:
            return None

        def _clean(v: Optional[str]) -> Optional[str]:
            v = (v or "").strip()
            return v or None

        return {
            "icon": _clean(icon),
            "name": _clean(name),
            "color": _clean(color),
            "link": _clean(link),
            "group": _clean(group),
            "sort": int(sort) if sort is not None else 0,
            "default": bool(default),
        }

    @staticmethod
    def _to_out(m: Menu) -> ClientMenuOut:
        qa = m.quick_action if isinstance(m.quick_action, dict) else None
        return ClientMenuOut(
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
            featureCode=m.feature_code,
            meta=None,
            createTime=(
                m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None
            ),
            quickActionEnabled=qa is not None,
            quickActionIcon=(qa or {}).get("icon"),
            quickActionName=(qa or {}).get("name"),
            quickActionColor=(qa or {}).get("color"),
            quickActionLink=(qa or {}).get("link"),
            quickActionGroup=(qa or {}).get("group"),
            quickActionSort=(qa or {}).get("sort"),
            quickActionDefault=bool((qa or {}).get("default", False)),
        )

    @staticmethod
    async def list_menus(
        db: AsyncSession,
        title: Optional[str] = None,
        path: Optional[str] = None,
        authority: Optional[str] = None,
        parent_id: Optional[int] = None,
        feature_code: Optional[str] = None,
    ) -> List[ClientMenuOut]:
        query = select(Menu).where(
            Menu.is_deleted == 0,
            Menu.app_type == "client",
        )
        if title:
            query = query.where(Menu.menu_name.contains(title))
        if path:
            query = query.where(Menu.path.contains(path))
        if authority:
            query = query.where(Menu.menu_code.contains(authority))
        if parent_id is not None:
            query = query.where(Menu.parent_id == parent_id)
        if feature_code:
            query = query.where(Menu.feature_code.contains(feature_code))

        query = query.order_by(Menu.sort_order, Menu.id)
        result = await db.execute(query)
        items = result.scalars().all()
        return [ClientMenuService._to_out(m) for m in items]

    @staticmethod
    async def create_menu(db: AsyncSession, data: ClientMenuCreate) -> None:
        menu = Menu(
            parent_id=data.parentId,
            menu_name=data.title,
            path=data.path,
            component=data.component,
            menu_type=data.menuType,
            sort_order=data.sortNumber,
            menu_code=data.authority,
            icon=data.icon,
            visible=0 if data.hide == 1 else 1,
            feature_code=data.featureCode,
            quick_action=ClientMenuService._build_quick_action(
                data.quickActionEnabled,
                data.quickActionIcon,
                data.quickActionName,
                data.quickActionColor,
                data.quickActionLink,
                data.quickActionGroup,
                data.quickActionSort,
                data.quickActionDefault,
            ),
            app_type="client",
            status=1,
        )
        db.add(menu)
        await db.flush()

    @staticmethod
    async def update_menu(db: AsyncSession, data: ClientMenuUpdate) -> None:
        result = await db.execute(
            select(Menu).where(
                Menu.id == data.menuId,
                Menu.app_type == "client",
                Menu.is_deleted == 0,
            )
        )
        menu = result.scalar_one_or_none()
        if not menu:
            raise BizException("菜单不存在")

        if data.parentId is not None:
            menu.parent_id = data.parentId
        if data.title is not None:
            menu.menu_name = data.title
        if data.path is not None:
            menu.path = data.path
        if data.component is not None:
            menu.component = data.component
        if data.menuType is not None:
            menu.menu_type = data.menuType
        if data.sortNumber is not None:
            menu.sort_order = data.sortNumber
        if data.authority is not None:
            menu.menu_code = data.authority
        if data.icon is not None:
            menu.icon = data.icon
        if data.hide is not None:
            menu.visible = 0 if data.hide == 1 else 1
        if data.featureCode is not None:
            menu.feature_code = data.featureCode

        # quickActionEnabled 提供时，整体重建 quick_action（表单保存会带全字段）
        if data.quickActionEnabled is not None:
            menu.quick_action = ClientMenuService._build_quick_action(
                data.quickActionEnabled,
                data.quickActionIcon,
                data.quickActionName,
                data.quickActionColor,
                data.quickActionLink,
                data.quickActionGroup,
                data.quickActionSort,
                data.quickActionDefault,
            )

        await db.flush()

    @staticmethod
    async def export_menus(db: AsyncSession) -> List[dict[str, Any]]:
        """导出 client 菜单为与 sys_menu.json 格式一致的扁平数组，
        供开发者同步到本地 sys_menu.json 后再执行 seed 脚本。"""
        query = (
            select(Menu)
            .where(Menu.is_deleted == 0, Menu.app_type == "client")
            .order_by(Menu.parent_id, Menu.sort_order, Menu.id)
        )
        result = await db.execute(query)
        items = result.scalars().all()
        rows: List[dict[str, Any]] = []
        for m in items:
            rows.append({
                "parent_id": m.parent_id,
                "menu_name": m.menu_name,
                "menu_code": m.menu_code or "",
                "menu_type": m.menu_type,
                "path": m.path,
                "component": m.component,
                "icon": m.icon,
                "sort_order": m.sort_order,
                "visible": m.visible,
                "status": m.status,
                "app_type": m.app_type,
                "feature_code": m.feature_code,
                "quick_action": m.quick_action,
                "id": m.id,
                "created_at": (
                    m.created_at.strftime("%d/%m/%Y %H:%M:%S")
                    if m.created_at else None
                ),
                "updated_at": (
                    m.updated_at.strftime("%d/%m/%Y %H:%M:%S")
                    if m.updated_at else None
                ),
                "is_deleted": m.is_deleted,
            })
        return rows

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: int) -> None:
        result = await db.execute(
            select(Menu).where(
                Menu.id == menu_id,
                Menu.app_type == "client",
                Menu.is_deleted == 0,
            )
        )
        menu = result.scalar_one_or_none()
        if not menu:
            raise BizException("菜单不存在")

        child_result = await db.execute(
            select(func.count()).where(
                Menu.parent_id == menu_id,
                Menu.app_type == "client",
                Menu.is_deleted == 0,
            )
        )
        child_count = child_result.scalar() or 0
        if child_count > 0:
            raise BizException("请先删除子菜单")

        menu.is_deleted = 1
        await db.flush()
