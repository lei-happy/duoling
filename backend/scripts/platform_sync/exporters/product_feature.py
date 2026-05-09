"""
导出功能清单（sys_product_feature）

接口: GET /api/console/product-feature （不传 page → 全量数组）
返回元素 camelCase（id, featureCode, featureName, module, description,
requiredTables, sortOrder, status, createdAt, updatedAt）。

输出快照：
  - 不导出 id（环境间不一致），以 feature_code 为业务主键
  - 按 sort_order, feature_code 稳定排序
  - required_tables 为 JSON 数组或 null（保持原值）
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..http_client import ConsoleClient


def _row_from_api(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "feature_code": item.get("featureCode"),
        "feature_name": item.get("featureName"),
        "module": item.get("module"),
        "description": item.get("description"),
        "required_tables": item.get("requiredTables"),
        "sort_order": int(item.get("sortOrder") or 0),
        "status": int(item.get("status") or 1),
    }


def export(client: ConsoleClient) -> List[Dict[str, Any]]:
    raw = client.get("/product-feature") or []
    rows = [_row_from_api(it) for it in raw]
    rows.sort(key=lambda x: (int(x.get("sort_order") or 0), x.get("feature_code") or ""))
    return rows
