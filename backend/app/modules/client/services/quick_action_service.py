"""
客户端工作台 - 快捷操作目录服务

读取平台库 sys_menu（app_type='client' 且 quick_action 非空），
映射为前端快捷操作注册项。权限/产品功能过滤仍由前端按 permission/feature 处理。
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.system.menu import Menu

DEFAULT_GROUP = "常用功能"


def _is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "//"))


def _split_link(link: Optional[str], fallback_path: Optional[str]) -> Dict[str, Any]:
    """将 link（可带 query）解析为 { type, path, query }；link 为空则用菜单 path"""
    raw = (link or "").strip() or (fallback_path or "").strip()
    if not raw:
        return {"type": "route", "path": "", "query": None}
    if _is_external(raw):
        return {"type": "external", "path": raw, "query": None}
    parsed = urlparse(raw)
    query: Optional[Dict[str, str]] = None
    if parsed.query:
        query = {k: v[0] for k, v in parse_qs(parsed.query).items() if v}
    return {"type": "route", "path": parsed.path or raw, "query": query or None}


class QuickActionService:

    @staticmethod
    async def list_registry(db: AsyncSession) -> List[Dict[str, Any]]:
        """返回全部启用了快捷操作的 client 菜单配置（前端再按权限/feature 过滤）"""
        result = await db.execute(
            select(Menu).where(
                Menu.is_deleted == 0,
                Menu.app_type == "client",
                Menu.quick_action.isnot(None),
            )
        )
        menus = result.scalars().all()

        # 顶层祖先名，用于分组回退
        by_id = {m.id: m for m in await QuickActionService._all_client_menus(db)}

        def _root_name(menu: Menu) -> str:
            cur = menu
            guard = 0
            while cur.parent_id and cur.parent_id in by_id and guard < 20:
                cur = by_id[cur.parent_id]
                guard += 1
            return cur.menu_name or DEFAULT_GROUP

        items: List[Dict[str, Any]] = []
        for m in menus:
            qa = m.quick_action if isinstance(m.quick_action, dict) else {}
            key = m.menu_code or f"menu.{m.id}"
            link_info = _split_link(qa.get("link"), m.path)
            items.append({
                "key": key,
                "title": qa.get("name") or m.menu_name,
                "image": qa.get("icon") or None,
                "color": qa.get("color") or None,
                "group": qa.get("group") or _root_name(m),
                "type": link_info["type"],
                "path": link_info["path"],
                "query": link_info["query"],
                "permission": m.menu_code or None,
                "feature": m.feature_code or None,
                "defaultVisible": bool(qa.get("default", False)),
                "sortOrder": qa.get("sort") if qa.get("sort") is not None else 0,
            })

        items.sort(key=lambda x: (x["sortOrder"], x["key"]))
        return items

    @staticmethod
    async def _all_client_menus(db: AsyncSession) -> List[Menu]:
        result = await db.execute(
            select(Menu).where(
                Menu.is_deleted == 0,
                Menu.app_type == "client",
            )
        )
        return list(result.scalars().all())
