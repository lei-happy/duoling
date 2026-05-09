"""
导出客户端菜单（app_type='client'）

接口: GET /api/console/system/client-menu/export
该接口服务端已经按 sys_menu.json 同构格式返回（snake_case，含 id/created_at/
updated_at 等）。本导出器主要职责：
  1. 过滤 is_deleted=1（导出接口已过滤，但兜底）
  2. 按 (parent_id, sort_order, id) 稳定排序，便于 git diff 友好
  3. 时间字段统一格式（dd/mm/YYYY HH:MM:SS → YYYY-MM-DD HH:MM:SS）
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from ..http_client import ConsoleClient


_TIME_FMT_OUT = "%Y-%m-%d %H:%M:%S"
_TIME_FMTS_IN = ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S")


def _normalize_time(s: Any) -> Any:
    if not s or not isinstance(s, str):
        return s
    s = s.strip()
    for fmt in _TIME_FMTS_IN:
        try:
            return datetime.strptime(s, fmt).strftime(_TIME_FMT_OUT)
        except ValueError:
            continue
    return s


def export(client: ConsoleClient) -> List[Dict[str, Any]]:
    rows = client.get("/system/client-menu/export") or []
    cleaned: List[Dict[str, Any]] = []
    for r in rows:
        if int(r.get("is_deleted", 0)) != 0:
            continue
        item = dict(r)
        # 兜底：app_type 必须是 client
        item["app_type"] = "client"
        item["created_at"] = _normalize_time(item.get("created_at"))
        item["updated_at"] = _normalize_time(item.get("updated_at"))
        # menu_code 空字符串 / None 统一为空字符串（与现有 sys_menu.json 兼容）
        if item.get("menu_code") is None:
            item["menu_code"] = ""
        cleaned.append(item)

    cleaned.sort(
        key=lambda x: (
            int(x.get("parent_id") or 0),
            int(x.get("sort_order") or 0),
            int(x.get("id") or 0),
        )
    )
    return cleaned
