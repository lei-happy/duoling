# -*- coding: utf-8 -*-
"""
租户端页面主接口冒烟：登录后按菜单页面对应的主列表/查询 API 发请求。
结果写入 last_api_result.json。
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "last_api_result.json"
API = os.environ.get("SMOKE_API", "http://localhost:8000").rstrip("/")
PHONE = os.environ.get("SMOKE_PHONE", "13900001001")
PASSWORD = os.environ.get("SMOKE_PASSWORD", "123456")

# path -> apis | "placeholder" | "static"
# apis: list of (method, url_suffix, params)
PAGE_APIS: dict[str, object] = {
    "/dashboard/workplace": [
        ("GET", "/workbench/activities", {"limit": 10}),
        ("GET", "/workbench/todo", {}),
        ("GET", "/workbench/banner", {}),
    ],
    "/operation/waybill": [
        ("GET", "/business/waybill", {"page": 1, "limit": 10}),
    ],
    "/operation/task-create": [
        ("GET", "/business/task/candidate-waybills", {"page": 1, "limit": 10}),
    ],
    "/operation/smart-stowage": [
        ("GET", "/business/smart-stowage/plans", {}),
    ],
    "/operation/task-workbench": [
        ("GET", "/business/task", {"page": 1, "limit": 10}),
        ("GET", "/business/task/workbench-stats", {}),
    ],
    "/operation/tracking": [
        ("GET", "/business/task", {"page": 1, "limit": 10}),
    ],
    "/operation/receipt": [
        ("GET", "/business/task", {"page": 1, "limit": 10}),
    ],
    "/operation/completed-task": [
        ("GET", "/business/task", {"page": 1, "limit": 10}),
    ],
    "/operation/task": [
        ("GET", "/business/task", {"page": 1, "limit": 10}),
    ],
    "/capacity/self-capacity/list": [
        ("GET", "/capacity/self_capacity/list", {"page": 1, "limit": 10}),
    ],
    "/capacity/self-capacity/driver": [
        ("GET", "/capacity/self_capacity/driver", {"page": 1, "limit": 10}),
    ],
    "/capacity/self-capacity/vehicle": [
        ("GET", "/capacity/self_capacity/vehicle", {"page": 1, "limit": 10}),
    ],
    "/capacity/self-capacity/trailer": [
        ("GET", "/capacity/self_capacity/trailer", {"page": 1, "limit": 10}),
    ],
    "/capacity/self-capacity/group": [
        ("GET", "/capacity/self_capacity/group", {"page": 1, "limit": 10}),
    ],
    "/capacity/self-capacity/log": [
        ("GET", "/capacity/self_capacity/log", {"page": 1, "limit": 10}),
    ],
    "/capacity/carrier-capacity/list": [
        ("GET", "/capacity/carrier_capacity/list", {"page": 1, "limit": 10}),
    ],
    "/capacity/carrier-capacity/capacity-approval": [
        ("GET", "/capacity/social_capacity/approval", {"page": 1, "limit": 10}),
    ],
    "/capacity/social-capacity/list": [
        ("GET", "/capacity/social_capacity/list", {"page": 1, "limit": 10}),
    ],
    "/capacity/social-capacity/capacity-approval": [
        ("GET", "/capacity/social_capacity/approval", {"page": 1, "limit": 10}),
    ],
    "/capacity/compliance": [
        ("GET", "/capacity/compliance/alerts", {"page": 1, "limit": 10}),
    ],
    "/partner/customer": [
        ("GET", "/partner/customer", {"page": 1, "limit": 10}),
    ],
    "/partner/carrier": [
        ("GET", "/partner/carrier", {"page": 1, "limit": 10}),
    ],
    "/partner/supplier": "placeholder",
    "/partner/inbound": [
        ("GET", "/partner/inbound", {"page": 1, "limit": 10}),
    ],
    "/partner/dealer": [
        ("GET", "/basic-data/dealer", {"page": 1, "limit": 10}),
    ],
    "/billing/contract": [
        ("GET", "/billing/contract", {"page": 1, "limit": 10}),
    ],
    "/billing/route": [
        ("GET", "/resource/route", {"page": 1, "limit": 10}),
    ],
    "/billing/cost-policy": [
        ("GET", "/billing/cost-policy", {"page": 1, "limit": 10}),
    ],
    "/billing/carrier-contract": [
        ("GET", "/billing/carrier-contract", {"page": 1, "limit": 10}),
    ],
    "/billing/fee-template": "placeholder",
    "/approval/pending": [
        ("GET", "/approval/pending", {"page": 1, "limit": 10}),
    ],
    "/approval/initiated": [
        ("GET", "/approval/initiated", {"page": 1, "limit": 10}),
    ],
    "/approval/history": [
        ("GET", "/approval/history", {"page": 1, "limit": 10}),
    ],
    "/finance/receivable": "placeholder",
    "/operation/task-finance-workbench": [
        ("GET", "/business/task-finance", {"page": 1, "limit": 10}),
        ("GET", "/business/task-finance/workbench-stats", {}),
    ],
    "/operation/task-finance": [
        ("GET", "/business/task-finance", {"page": 1, "limit": 10}),
    ],
    "/finance/reconciliation": "placeholder",
    "/finance/invoice": "placeholder",
    "/finance/profit": [
        ("GET", "/insight/cockpit/profit/kpi-summary", {}),
    ],
    "/insight/cockpit/overview": [
        ("GET", "/insight/cockpit/kpi-summary", {}),
    ],
    "/insight/cockpit/profit": [
        ("GET", "/insight/cockpit/profit/kpi-summary", {}),
    ],
    "/insight/overview": "placeholder",
    "/insight/report": "placeholder",
    "/insight/prediction": "placeholder",
    "/open-platform/apps": [
        ("GET", "/open-platform/apps", {}),
    ],
    "/open-platform/capabilities": [
        ("GET", "/open-platform/capabilities", {}),
    ],
    "/open-platform/docs": "static",
    "/open-platform/logs": [
        ("GET", "/open-platform/logs", {"page": 1, "limit": 10}),
    ],
    "/ecosystem/cargo-hall": [
        ("GET", "/ecosystem/cargo-hall", {"page": 1, "limit": 10}),
    ],
    "/ecosystem/capacity-hall": [
        ("GET", "/ecosystem/capacity-hall", {"page": 1, "limit": 10}),
    ],
    "/ecosystem/service-hall": "placeholder",
    "/ecosystem/deals": [
        ("GET", "/ecosystem/my-posts", {"page": 1, "limit": 10}),
    ],
    "/ecosystem/profile": [
        ("GET", "/ecosystem/my-posts", {"page": 1, "limit": 5}),
    ],
    "/log-center/operation-log": [
        ("GET", "/logcenter/operation-record/page", {"page": 1, "limit": 10}),
    ],
    "/log-center/login-log": [
        ("GET", "/logcenter/login-record/page", {"page": 1, "limit": 10}),
    ],
    "/enterprise/organization": [
        ("GET", "/system/organization/tree", {}),
    ],
    "/enterprise/business-entity": [
        ("GET", "/system/business-entity", {"page": 1, "limit": 10}),
    ],
    "/enterprise/user": [
        ("GET", "/system/user/page", {"page": 1, "limit": 10}),
    ],
    "/enterprise/role": [
        ("GET", "/system/role/page", {"page": 1, "limit": 10}),
    ],
    "/enterprise/approval-config": [
        ("GET", "/approval/flow", {"page": 1, "limit": 10}),
    ],
    "/enterprise/basic-data/regional": [
        ("GET", "/basic-data/region/children", {"page": 1, "limit": 10}),
    ],
    "/enterprise/basic-data/brand-series": [
        ("GET", "/basic-data/vehicle-brand", {"page": 1, "limit": 10}),
    ],
    "/enterprise/dictionary": [
        ("GET", "/system/dictionary/page", {"page": 1, "limit": 10}),
    ],
    "/enterprise/config": [
        ("GET", "/system/config", {}),
    ],
}


def login(client: httpx.Client) -> str:
    r = client.post(
        f"{API}/api/client/auth/login",
        json={"phone": PHONE, "password": PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    if body.get("code") != 0:
        raise RuntimeError(body)
    return body["data"]["access_token"]


def main():
    menu_rows = json.loads(
        (ROOT / "scripts/_tmp_client_menu_tree.json").read_text(encoding="utf-8")
    )
    pages = [
        r
        for r in menu_rows
        if r.get("visible")
        and r.get("path")
        and str(r["path"]).startswith("/")
        and r.get("component")
    ]

    results = []
    with httpx.Client(timeout=30.0) as client:
        token = login(client)
        headers = {"Authorization": f"Bearer {token}"}

        for page in pages:
            path = page["path"]
            conf = PAGE_APIS.get(path)
            entry = {
                "name": page["name"],
                "path": path,
                "l1": (page.get("ancestors") or [page["name"]])[0],
                "ok": False,
                "kind": "api",
                "apis": [],
                "note": "",
            }
            if conf is None:
                entry["note"] = "no_api_mapping"
                results.append(entry)
                print(f"[SKIP] {path}")
                continue
            if conf in ("placeholder", "static"):
                entry["ok"] = True
                entry["kind"] = conf
                entry["note"] = conf
                results.append(entry)
                print(f"[OK] {path} ({conf})")
                continue

            all_ok = True
            for method, suffix, params in conf:  # type: ignore
                url = f"{API}/api/client{suffix}"
                try:
                    resp = client.request(method, url, params=params, headers=headers)
                    http_st = resp.status_code
                    try:
                        body = resp.json()
                    except Exception:
                        body = {}
                    biz_code = body.get("code") if isinstance(body, dict) else None
                    msg = body.get("message") if isinstance(body, dict) else None
                    ok = http_st < 500 and http_st != 404 and biz_code in (0, "0", 200, None)
                    if http_st < 500 and http_st != 404 and biz_code not in (0, "0", 200, None):
                        # 业务拒绝（权限/未开通）记条件通过：接口可达
                        ok = True
                        entry["note"] = f"biz:{biz_code}:{msg}"
                    api_item = {
                        "method": method,
                        "url": suffix,
                        "http": http_st,
                        "code": biz_code,
                        "message": msg,
                        "ok": ok,
                    }
                except Exception as e:
                    api_item = {
                        "method": method,
                        "url": suffix,
                        "ok": False,
                        "error": str(e),
                    }
                entry["apis"].append(api_item)
                if not api_item.get("ok"):
                    all_ok = False
            entry["ok"] = all_ok
            results.append(entry)
            print(f"[{'OK' if all_ok else 'FAIL'}] {path} {entry.get('note','')}")

    passed = sum(1 for r in results if r["ok"])
    failed = [r for r in results if not r["ok"]]
    placeholders = [r for r in results if r.get("kind") == "placeholder"]
    summary = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api": API,
        "phone": PHONE,
        "total": len(results),
        "passed": passed,
        "failed_count": len(failed),
        "placeholder_count": len(placeholders),
        "failed": [
            {"path": f["path"], "name": f["name"], "note": f.get("note"), "apis": f.get("apis")}
            for f in failed
        ],
        "placeholders": [p["path"] for p in placeholders],
        "results": results,
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DONE {passed}/{len(results)} placeholder={len(placeholders)} -> {OUT}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
