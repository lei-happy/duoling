"""
导出 Console 平台端菜单（app_type='platform'）

接口: GET /api/console/system/menu
返回字段为 camelCase 的 MenuOut（menuId/parentId/title/path/component/menuType/
sortNumber/authority/icon/hide/meta/createTime），不含 visible/feature_code/
status 等 DB 字段。本导出器把它反规范化成与 client_menu.json 同构的 snake_case
结构，便于 seed 脚本统一处理。

字段映射（API → 快照）：
  menuId       → id
  parentId     → parent_id
  title        → menu_name
  authority    → menu_code（空串或 None）
  menuType     → menu_type
  sortNumber   → sort_order
  hide         → visible（hide=1 → visible=0）
  createTime   → created_at
  -            → app_type='platform' / status=1 / is_deleted=0 / feature_code=None
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..http_client import ConsoleClient


def _row_from_api(item: Dict[str, Any]) -> Dict[str, Any]:
    hide = int(item.get("hide") or 0)
    return {
        "parent_id": int(item.get("parentId") or 0),
        "menu_name": item.get("title") or "",
        "menu_code": item.get("authority") or "",
        "menu_type": int(item.get("menuType") or 0),
        "path": item.get("path"),
        "component": item.get("component"),
        "icon": item.get("icon"),
        "sort_order": int(item.get("sortNumber") or 0),
        "visible": 0 if hide == 1 else 1,
        "status": 1,
        "app_type": "platform",
        # 平台菜单接口暂未暴露 feature_code，统一置空保持 schema 对齐
        "feature_code": None,
        "id": int(item.get("menuId")),
        "created_at": item.get("createTime"),
        # API 不返回 updated_at，留空 seed 时不会覆盖
        "updated_at": item.get("createTime"),
        "is_deleted": 0,
    }


def export(client: ConsoleClient) -> List[Dict[str, Any]]:
    raw = client.get("/system/menu") or []
    rows = [_row_from_api(it) for it in raw]
    rows.sort(
        key=lambda x: (
            int(x.get("parent_id") or 0),
            int(x.get("sort_order") or 0),
            int(x.get("id") or 0),
        )
    )
    return rows
