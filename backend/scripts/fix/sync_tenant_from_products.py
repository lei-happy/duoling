"""
以 sys_tenant_product 为唯一权威，重算并修正 sys_tenant 的反范式字段：
  - status：有有效授权 → 1（正常），无有效授权 → 3（已过期）
  - expire_time：取所有有效授权 end_time 的最晚值；存在永久授权则置 NULL
  - menu_version：发生任何变化时 +1，触发客户端重新拉取菜单

适用场景（基于本次定位的真实问题）：
    运营 / 测试 直连数据库改 sys_tenant_product（如把 1001 改为 pro）
    后，sys_tenant.status 与 sys_tenant.expire_time 不会自动同步，
    导致：
      - 客户列表 status=3 → 在「试用 / 付费」tab 不显示
      - 列表「到期时间」字段仍是旧值
      - 客户端菜单 menu_version 不变 → 不刷新

后端 check_expirations 已增加上行恢复逻辑（30s 定时器），
本脚本提供「立即手工触发 + 可指定单租户」能力，避免等定时任务。

用法：
    # 修复单个租户
    python backend/scripts/fix/sync_tenant_from_products.py --tenant 1001

    # 修复全部租户
    python backend/scripts/fix/sync_tenant_from_products.py --all

    # 仅预览不写库
    python backend/scripts/fix/sync_tenant_from_products.py --all --dry-run
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


def _fetch_tenants(conn, tenant_code: Optional[str]) -> List[dict]:
    if tenant_code:
        sql = text(
            "SELECT id, tenant_code, status, expire_time, menu_version "
            "FROM sys_tenant WHERE is_deleted = 0 AND tenant_code = :tc"
        )
        rows = conn.execute(sql, {"tc": tenant_code}).mappings().all()
    else:
        sql = text(
            "SELECT id, tenant_code, status, expire_time, menu_version "
            "FROM sys_tenant WHERE is_deleted = 0"
        )
        rows = conn.execute(sql).mappings().all()
    return [dict(r) for r in rows]


def _fetch_active_products(conn, tenant_id: int, now: datetime) -> List[dict]:
    sql = text(
        "SELECT id, version_code, end_time "
        "FROM sys_tenant_product "
        "WHERE tenant_id = :tid AND is_deleted = 0 AND status = 1 "
        "AND (end_time IS NULL OR end_time > :now)"
    )
    rows = conn.execute(sql, {"tid": tenant_id, "now": now}).mappings().all()
    return [dict(r) for r in rows]


def _calc_target(active_products: List[dict]) -> dict:
    if not active_products:
        return {"status": 3, "expire_time": None}
    if any(p["end_time"] is None for p in active_products):
        return {"status": 1, "expire_time": None}
    return {
        "status": 1,
        "expire_time": max(p["end_time"] for p in active_products),
    }


def sync(tenant_code: Optional[str], all_tenants: bool, dry_run: bool) -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)
    now = datetime.now()

    with engine.connect() as conn:
        tenants = _fetch_tenants(conn, None if all_tenants else tenant_code)
        if not tenants:
            print(f"[WARN] 未找到匹配租户：tenant_code={tenant_code}, all={all_tenants}")
            return

        affected = 0
        for t in tenants:
            actives = _fetch_active_products(conn, t["id"], now)
            target = _calc_target(actives)

            need_update = (
                t["status"] != target["status"]
                or t["expire_time"] != target["expire_time"]
            )
            tag = "CHG" if need_update else "ok "
            actives_brief = ", ".join(
                f"{p['version_code']}@{p['end_time']}" for p in actives
            ) or "<none>"
            print(
                f"[{tag}] {t['tenant_code']:<10} "
                f"status: {t['status']} -> {target['status']}, "
                f"expire: {t['expire_time']} -> {target['expire_time']}, "
                f"mv: {t['menu_version']}{'+1' if need_update else ''}, "
                f"actives: [{actives_brief}]"
            )

            if need_update and not dry_run:
                conn.execute(
                    text(
                        "UPDATE sys_tenant "
                        "SET status = :st, expire_time = :et, "
                        "    menu_version = COALESCE(menu_version, 0) + 1, "
                        "    updated_at = NOW() "
                        "WHERE id = :tid"
                    ),
                    {
                        "st": target["status"],
                        "et": target["expire_time"],
                        "tid": t["id"],
                    },
                )
                affected += 1

        if not dry_run:
            conn.commit()
            print(f"\n[OK] 已修正 {affected} / {len(tenants)} 个租户")
        else:
            print(f"\n[DRY-RUN] 预计修正 {sum(1 for _ in tenants)} 中的若干条，未写库")

    engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="按 sys_tenant_product 修正 sys_tenant 反范式字段"
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--tenant", help="单租户 tenant_code，如 1001")
    g.add_argument("--all", action="store_true", help="修复全部租户")
    parser.add_argument("--dry-run", action="store_true", help="仅预览不写库")
    args = parser.parse_args()

    sync(
        tenant_code=args.tenant,
        all_tenants=args.all,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
