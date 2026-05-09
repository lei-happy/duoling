"""
导出版本-功能映射（sys_version_feature）

策略：
  1. GET /api/console/product-version 拿所有 versionCode + id
  2. 对每个版本 GET /api/console/product-feature/version/{id} 拿到该版本的 featureCode 列表
  3. 输出 dict：{ version_code: [feature_code, feature_code, ...] }
     用 version_code & feature_code 作为业务主键，跨环境稳定。

输出形如：
{
    "lite":     ["base_dashboard", "base_user", ...],
    "basic":    [...],
    "standard": [...],
    "pro":      [...],
    "enterprise": [...]
}
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..http_client import ConsoleClient

PAGE_SIZE_MAX = 200


def _list_versions(client: ConsoleClient) -> List[Dict[str, Any]]:
    """复用产品版本接口拿 (id, versionCode) 列表"""
    versions: List[Dict[str, Any]] = []
    page = 1
    while True:
        payload = client.get(
            "/product-version", params={"page": page, "page_size": PAGE_SIZE_MAX}
        ) or {}
        items = payload.get("list") or []
        for it in items:
            vid = it.get("id")
            vcode = it.get("versionCode")
            if vid is not None and vcode:
                versions.append({"id": int(vid), "code": vcode})
        total = int(payload.get("total") or 0)
        if len(versions) >= total or not items:
            break
        page += 1
        if page > 100:
            break
    return versions


def export(client: ConsoleClient) -> Dict[str, List[str]]:
    versions = _list_versions(client)
    result: Dict[str, List[str]] = {}
    for v in versions:
        items = client.get(f"/product-feature/version/{v['id']}") or []
        codes = sorted(
            {it.get("featureCode") for it in items if it.get("featureCode")}
        )
        result[v["code"]] = list(codes)

    # dict 顺序稳定（按 version_code 字母序），git diff 友好
    return {k: result[k] for k in sorted(result.keys())}
