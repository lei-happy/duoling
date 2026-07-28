# -*- coding: utf-8 -*-
"""
租户端菜单 UI 冒烟：登录后逐路由访问。
优先使用系统 Chrome（channel=chrome），避免下载 Playwright Chromium。
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[2]
MENU_JSON = ROOT / "scripts" / "_tmp_client_menu_tree.json"
OUT_JSON = Path(__file__).resolve().parent / "last_ui_result.json"

BASE = os.environ.get("SMOKE_BASE", "http://localhost:5174").rstrip("/")
API = os.environ.get("SMOKE_API", "http://localhost:8000").rstrip("/")
PHONE = os.environ.get("SMOKE_PHONE", "13900001001")
PASSWORD = os.environ.get("SMOKE_PASSWORD", "123456")


def load_pages():
    rows = json.loads(MENU_JSON.read_text(encoding="utf-8"))
    return [
        r
        for r in rows
        if r.get("visible")
        and r.get("path")
        and str(r["path"]).startswith("/")
        and r.get("component")
    ]


def api_login() -> dict:
    r = httpx.post(
        f"{API}/api/client/auth/login",
        json={"phone": PHONE, "password": PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    if body.get("code") != 0:
        raise RuntimeError(body)
    return body["data"]


def main():
    pages = load_pages()
    print(f"[ui] pages={len(pages)} base={BASE}")
    token_data = api_login()
    token = token_data["access_token"]
    refresh = token_data.get("refresh_token") or ""

    from playwright.sync_api import sync_playwright

    results = []
    failed = []

    with sync_playwright() as p:
        # 优先本机 Chrome，避免 playwright chromium 下载
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
            print("[ui] using channel=chrome")
        except Exception as e1:
            print(f"[ui] chrome channel failed: {e1}; try msedge")
            try:
                browser = p.chromium.launch(channel="msedge", headless=True)
                print("[ui] using channel=msedge")
            except Exception as e2:
                print(f"[ui] msedge failed: {e2}; try bundled chromium")
                browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()
        api_5xx = []

        def on_response(resp):
            if "/api/client/" in resp.url and resp.status >= 500:
                api_5xx.append({"url": resp.url, "status": resp.status})

        page.on("response", on_response)

        page.goto(f"{BASE}/login", wait_until="domcontentloaded", timeout=90000)
        page.evaluate(
            """([token, refresh]) => {
              localStorage.setItem('token', token);
              localStorage.setItem('refresh_token', refresh);
              sessionStorage.setItem('token', token);
              sessionStorage.setItem('refresh_token', refresh);
            }""",
            [token, refresh],
        )

        # 表单登录兜底（动态路由依赖完整登录态）
        page.goto(f"{BASE}/login", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(1500)
        try:
            phone_input = page.locator('input[type="text"], input[type="tel"]').first
            pwd_input = page.locator('input[type="password"]').first
            if phone_input.count() and pwd_input.count():
                phone_input.fill(PHONE)
                pwd_input.fill(PASSWORD)
                remember = page.locator(".el-checkbox").first
                if remember.count():
                    try:
                        remember.click(timeout=1000)
                    except Exception:
                        pass
                page.locator('button:has-text("登录")').first.click()
                page.wait_for_timeout(5000)
        except Exception as e:
            print(f"[ui] form login skip: {e}")

        page.evaluate(
            """([token, refresh]) => {
              localStorage.setItem('token', token);
              localStorage.setItem('refresh_token', refresh);
            }""",
            [token, refresh],
        )
        page.goto(f"{BASE}/dashboard/workplace", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2000)
        if "/login" in page.url:
            print("[ui] WARN still on login after auth injection")

        for r in pages:
            path = r["path"]
            name = r["name"]
            api_5xx.clear()
            entry = {
                "name": name,
                "path": path,
                "l1": (r.get("ancestors") or [name])[0],
                "ok": False,
                "url": "",
                "error": "",
                "api_5xx": [],
            }
            try:
                page.goto(f"{BASE}{path}", wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(1200)
                entry["url"] = page.url
                text = ""
                try:
                    text = page.locator("body").inner_text(timeout=5000)[:1500]
                except Exception:
                    pass

                # 仅当落在登录路由本身时算失败（避免 /log-center/login-log 误判）
                path_only = urlparse(page.url).path.rstrip("/") or "/"
                if path_only == "/login":
                    entry["error"] = "redirected_to_login"
                elif any(
                    s in text[:300]
                    for s in ("页面不存在", "Cannot GET", "Failed to fetch")
                ):
                    entry["error"] = "error_page"
                elif api_5xx:
                    entry["error"] = "api_5xx"
                    entry["api_5xx"] = api_5xx[:]
                else:
                    has_app = page.locator("#app").count() > 0
                    entry["ok"] = has_app

                if not entry["ok"] and not entry["error"]:
                    entry["error"] = "unknown"
            except Exception as e:
                entry["error"] = str(e)[:300]

            results.append(entry)
            flag = "OK" if entry["ok"] else "FAIL"
            print(f"[{flag}] {entry['l1']}/{name} {path} {entry.get('error')}")
            if not entry["ok"]:
                failed.append(entry)

        browser.close()

    summary = {
        "ok": len(failed) == 0,
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "api": API,
        "base": BASE,
        "phone": PHONE,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "failures": failed,
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ui] done {summary['passed']}/{summary['total']} -> {OUT_JSON}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
