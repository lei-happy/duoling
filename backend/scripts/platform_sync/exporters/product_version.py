"""
导出产品版本（sys_product_version）

接口: GET /api/console/product-version?page=1&page_size=200
返回 {list, total, page, page_size}，list 元素 camelCase（id, versionCode,
versionName, description, features, maxUsers, maxVehicles, price, sortOrder,
status, createdAt, updatedAt）。

本导出器：
  1. 自动翻页拉全量
  2. camelCase → snake_case
  3. 按 sort_order, version_code 稳定排序
  4. **不导出** id（环境间不一致），仅以 version_code 作为业务主键
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..http_client import ConsoleClient

PAGE_SIZE_MAX = 200


def _row_from_api(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "version_code": item.get("versionCode"),
        "version_name": item.get("versionName"),
        "description": item.get("description"),
        "features": item.get("features"),
        "max_users": int(item.get("maxUsers") or 0),
        "max_vehicles": int(item.get("maxVehicles") or 0),
        "price": item.get("price"),
        "sort_order": int(item.get("sortOrder") or 0),
        "status": int(item.get("status") or 1),
    }


def export(client: ConsoleClient) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    page = 1
    while True:
        payload = client.get(
            "/product-version", params={"page": page, "page_size": PAGE_SIZE_MAX}
        ) or {}
        items = payload.get("list") or []
        rows.extend(_row_from_api(it) for it in items)

        total = int(payload.get("total") or 0)
        if len(rows) >= total or not items:
            break
        page += 1
        if page > 100:  # 安全阀
            break

    rows.sort(key=lambda x: (int(x.get("sort_order") or 0), x.get("version_code") or ""))
    return rows
