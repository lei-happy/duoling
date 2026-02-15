"""
菜单管理服务
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.menu import Menu
from app.modules.console.schemas.menu import MenuCreate, MenuUpdate, MenuOut


class MenuService:
    """菜单管理服务"""

    @staticmethod
    def _to_out(m: Menu) -> MenuOut:
        """将 ORM 模型转换为输出 Schema"""
        return MenuOut(
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
            meta=None,
            createTime=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        )

    @staticmethod
    async def list_menus(
        db: AsyncSession,
        title: Optional[str] = None,
        path: Optional[str] = None,
        authority: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> List[MenuOut]:
        """查询菜单列表（扁平数组，前端自行构建树）"""
        query = select(Menu).where(
            Menu.is_deleted == 0,
            Menu.app_type == "platform",
        )
        if title:
            query = query.where(Menu.menu_name.contains(title))
        if path:
            query = query.where(Menu.path.contains(path))
        if authority:
            query = query.where(Menu.menu_code.contains(authority))
        if parent_id is not None:
            query = query.where(Menu.parent_id == parent_id)

        query = query.order_by(Menu.sort_order, Menu.id)
        result = await db.execute(query)
        items = result.scalars().all()
        return [MenuService._to_out(m) for m in items]

    @staticmethod
    async def page_menus(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        title: Optional[str] = None,
    ) -> dict:
        """分页查询菜单"""
        query = select(Menu).where(
            Menu.is_deleted == 0,
            Menu.app_type == "platform",
        )
        if title:
            query = query.where(Menu.menu_name.contains(title))

        # 总数
        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        # 分页
        query = query.order_by(Menu.sort_order, Menu.id)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return {
            "list": [MenuService._to_out(m) for m in items],
            "count": count,
        }

    @staticmethod
    async def create_menu(db: AsyncSession, data: MenuCreate) -> None:
        """新增菜单"""
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
            app_type="platform",
            status=1,
        )
        db.add(menu)
        await db.flush()

    @staticmethod
    async def update_menu(db: AsyncSession, data: MenuUpdate) -> None:
        """修改菜单"""
        result = await db.execute(
            select(Menu).where(Menu.id == data.menuId, Menu.is_deleted == 0)
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

        await db.flush()

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: int) -> None:
        """删除菜单（软删除）"""
        result = await db.execute(
            select(Menu).where(Menu.id == menu_id, Menu.is_deleted == 0)
        )
        menu = result.scalar_one_or_none()
        if not menu:
            raise BizException("菜单不存在")

        # 检查是否有子菜单
        child_result = await db.execute(
            select(func.count()).where(
                Menu.parent_id == menu_id, Menu.is_deleted == 0
            )
        )
        child_count = child_result.scalar() or 0
        if child_count > 0:
            raise BizException("请先删除子菜单")

        menu.is_deleted = 1
        await db.flush()
