"""
客户端菜单结构重组（一次性，幂等）

对应 client_menu.json 变更：
  1. 新增一级「日志中心」(id=814)
  2. 数据字典 (174) 归入「数据管理」(320)
  3. 操作/登录记录 (175/176) 挂到日志中心，path 迁移至 /log-center/...

执行内容（按顺序）：
  Step 1: 平台库 sys_menu 写入/修正上述菜单
  Step 2: 各租户库 biz_role_menu 补全父级菜单（814、320）
  Step 3: sys_tenant.menu_version + 1，强制客户端刷新菜单

用法：
    cd backend
    python scripts/fix/reorganize_client_menus.py
    python scripts/fix/reorganize_client_menus.py --dry-run
    python scripts/fix/reorganize_client_menus.py --tenant-code demo001
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from app.core.config import get_settings

LOG_CENTER_ID = 814
BASIC_DATA_ID = 320
DICT_MENU_ID = 174
OPERATION_LOG_ID = 175
LOGIN_LOG_ID = 176

NEW_LOG_CENTER = {
    "id": LOG_CENTER_ID,
    "parent_id": 0,
    "menu_name": "日志中心",
    "menu_code": "log-center",
    "menu_type": 0,
    "path": "/log-center",
    "component": None,
    "icon": "rizhizhongxin",
    "sort_order": 850,
    "visible": 1,
    "status": 1,
    "app_type": "client",
    "feature_code": "base_log",
}

MENU_UPDATES: list[dict] = [
    {
        "id": DICT_MENU_ID,
        "parent_id": BASIC_DATA_ID,
        "path": "/enterprise/dictionary",
        "component": "/enterprise/dictionary/index",
        "sort_order": 20,
        "menu_name": "数据字典",
        "menu_code": "system:dictionary",
        "feature_code": "base_dict",
    },
    {
        "id": OPERATION_LOG_ID,
        "parent_id": LOG_CENTER_ID,
        "path": "/log-center/operation-log",
        "component": "/log-center/operation-log/index",
        "sort_order": 0,
        "menu_name": "操作记录",
        "menu_code": "system:operation-record",
        "feature_code": "base_log",
    },
    {
        "id": LOGIN_LOG_ID,
        "parent_id": LOG_CENTER_ID,
        "path": "/log-center/login-log",
        "component": "/log-center/login-log/index",
        "sort_order": 10,
        "menu_name": "登录记录",
        "menu_code": "system:login-record",
        "feature_code": "base_log",
    },
]

# 子菜单 id -> 需补全的父级菜单 id
PARENT_BACKFILL: dict[int, int] = {
    OPERATION_LOG_ID: LOG_CENTER_ID,
    LOGIN_LOG_ID: LOG_CENTER_ID,
    DICT_MENU_ID: BASIC_DATA_ID,
}


def _build_platform_engine():
    settings = get_settings()
    return create_engine(settings.platform_db_url_sync)


def _table_exists(conn: Connection, table_name: str) -> bool:
    return bool(
        conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name = :t"
            ),
            {"t": table_name},
        ).scalar()
    )


def _get_tenant_codes(conn: Connection, tenant_code: Optional[str]) -> list[str]:
    if tenant_code:
        rows = conn.execute(
            text(
                "SELECT tenant_code FROM sys_tenant "
                "WHERE is_deleted = 0 AND tenant_code = :tc"
            ),
            {"tc": tenant_code},
        ).fetchall()
    else:
        rows = conn.execute(
            text(
                "SELECT tenant_code FROM sys_tenant "
                "WHERE is_deleted = 0 ORDER BY tenant_code"
            )
        ).fetchall()
    return [r[0] for r in rows]


def step1_upsert_menus(conn: Connection, dry_run: bool) -> None:
    print()
    print("=" * 60)
    print("Step 1: 平台库 sys_menu 写入/修正菜单结构")
    print("=" * 60)

    row = conn.execute(
        text("SELECT id FROM sys_menu WHERE id = :id"),
        {"id": LOG_CENTER_ID},
    ).fetchone()

    if row:
        print(f"  [SKIP] id={LOG_CENTER_ID} 日志中心 已存在")
    else:
        prefix = "DRY-RUN" if dry_run else "INSERT"
        print(f"  [{prefix}] INSERT id={LOG_CENTER_ID} 日志中心")
        if not dry_run:
            conn.execute(
                text(
                    "INSERT INTO sys_menu ("
                    "  id, parent_id, menu_name, menu_code, menu_type, path, component, "
                    "  icon, sort_order, visible, status, app_type, feature_code, "
                    "  created_at, updated_at, is_deleted"
                    ") VALUES ("
                    "  :id, :parent_id, :menu_name, :menu_code, :menu_type, :path, :component, "
                    "  :icon, :sort_order, :visible, :status, :app_type, :feature_code, "
                    "  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0"
                    ")"
                ),
                NEW_LOG_CENTER,
            )

    updated = 0
    for item in MENU_UPDATES:
        existing = conn.execute(
            text(
                "SELECT id, parent_id, path, component, sort_order, menu_code, "
                "feature_code, is_deleted FROM sys_menu WHERE id = :id"
            ),
            {"id": item["id"]},
        ).fetchone()
        if not existing:
            print(f"  [WARN] id={item['id']} ({item['menu_name']}) 不存在，跳过")
            continue

        diffs = []
        if int(existing.parent_id) != item["parent_id"]:
            diffs.append(f"parent_id {existing.parent_id} -> {item['parent_id']}")
        if (existing.path or "") != item["path"]:
            diffs.append(f"path {existing.path!r} -> {item['path']!r}")
        if (existing.component or "") != item["component"]:
            diffs.append(f"component {existing.component!r} -> {item['component']!r}")
        if int(existing.sort_order) != item["sort_order"]:
            diffs.append(f"sort_order {existing.sort_order} -> {item['sort_order']}")
        if int(existing.is_deleted) == 1:
            diffs.append("is_deleted 1 -> 0")

        if not diffs:
            print(f"  [SKIP] id={item['id']:<3d} {item['menu_name']:<8s} 已是目标状态")
            continue

        prefix = "DRY-RUN" if dry_run else "UPDATE"
        print(f"  [{prefix}] id={item['id']:<3d} {item['menu_name']:<8s}  " + "; ".join(diffs))
        if not dry_run:
            conn.execute(
                text(
                    "UPDATE sys_menu SET "
                    "  parent_id = :parent_id, path = :path, component = :component, "
                    "  sort_order = :sort_order, menu_code = :menu_code, "
                    "  feature_code = :feature_code, menu_name = :menu_name, "
                    "  is_deleted = 0, updated_at = CURRENT_TIMESTAMP "
                    "WHERE id = :id"
                ),
                item,
            )
            updated += 1
    print(f"  -> 更新 {updated} 条已有菜单")


def step2_backfill_role_menus(
    platform_conn: Connection,
    tenant_codes: list[str],
    dry_run: bool,
) -> None:
    print()
    print("=" * 60)
    print("Step 2: 租户库 biz_role_menu 补全父级菜单权限")
    print("=" * 60)

    if not tenant_codes:
        print("  [INFO] 无活跃租户，跳过")
        return

    settings = get_settings()
    total_inserted = 0

    for tc in tenant_codes:
        tenant_url = settings.tenant_db_url_sync(tc)
        tenant_engine = create_engine(tenant_url)
        try:
            with tenant_engine.connect() as tconn:
                if not _table_exists(tconn, "biz_role_menu"):
                    print(f"  [SKIP] {tc}: biz_role_menu 表不存在")
                    continue

                inserted = 0
                for child_id, parent_id in PARENT_BACKFILL.items():
                    roles = tconn.execute(
                        text(
                            "SELECT DISTINCT role_id FROM biz_role_menu "
                            "WHERE menu_id = :child_id AND is_deleted = 0"
                        ),
                        {"child_id": child_id},
                    ).fetchall()
                    for (role_id,) in roles:
                        exists = tconn.execute(
                            text(
                                "SELECT id FROM biz_role_menu "
                                "WHERE role_id = :role_id AND menu_id = :menu_id "
                                "AND is_deleted = 0 LIMIT 1"
                            ),
                            {"role_id": role_id, "menu_id": parent_id},
                        ).fetchone()
                        if exists:
                            continue
                        soft_deleted = tconn.execute(
                            text(
                                "SELECT id FROM biz_role_menu "
                                "WHERE role_id = :role_id AND menu_id = :menu_id "
                                "AND is_deleted = 1 LIMIT 1"
                            ),
                            {"role_id": role_id, "menu_id": parent_id},
                        ).fetchone()
                        prefix = "DRY-RUN" if dry_run else "INSERT"
                        print(
                            f"  [{prefix}] {tc} role={role_id} "
                            f"补勾父级 menu_id={parent_id} (子菜单 {child_id})"
                        )
                        if not dry_run:
                            if soft_deleted:
                                tconn.execute(
                                    text(
                                        "UPDATE biz_role_menu SET is_deleted = 0, "
                                        "updated_at = CURRENT_TIMESTAMP "
                                        "WHERE id = :id"
                                    ),
                                    {"id": int(soft_deleted.id)},
                                )
                            else:
                                tconn.execute(
                                    text(
                                        "INSERT INTO biz_role_menu ("
                                        "  role_id, menu_id, created_at, updated_at, is_deleted"
                                        ") VALUES ("
                                        "  :role_id, :menu_id, "
                                        "  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0"
                                        ")"
                                    ),
                                    {"role_id": role_id, "menu_id": parent_id},
                                )
                            inserted += 1
                if not dry_run:
                    tconn.commit()
                total_inserted += inserted
                if inserted == 0:
                    print(f"  [OK] {tc}: 无需补全")
        finally:
            tenant_engine.dispose()

    print(f"  -> 共补全 {total_inserted} 条角色-菜单关联")


def step3_bump_menu_version(conn: Connection, dry_run: bool) -> None:
    print()
    print("=" * 60)
    print("Step 3: sys_tenant.menu_version + 1")
    print("=" * 60)
    cnt = conn.execute(
        text("SELECT COUNT(*) FROM sys_tenant WHERE is_deleted = 0")
    ).scalar() or 0
    prefix = "DRY-RUN" if dry_run else "BUMP"
    print(f"  [{prefix}] 共 {cnt} 个活跃租户，menu_version + 1")
    if not dry_run:
        conn.execute(
            text(
                "UPDATE sys_tenant SET menu_version = COALESCE(menu_version, 0) + 1 "
                "WHERE is_deleted = 0"
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description="客户端菜单结构重组：日志中心一级菜单 + 基础数据归类"
    )
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写库")
    parser.add_argument(
        "--tenant-code",
        help="仅处理指定租户（Step 2）；默认处理全部活跃租户",
    )
    args = parser.parse_args()

    print("客户端菜单结构重组脚本")
    print(f"  dry_run = {args.dry_run}")

    engine = _build_platform_engine()
    try:
        with engine.connect() as conn:
            step1_upsert_menus(conn, args.dry_run)
            tenant_codes = _get_tenant_codes(conn, args.tenant_code)
            step2_backfill_role_menus(conn, tenant_codes, args.dry_run)
            step3_bump_menu_version(conn, args.dry_run)
            if not args.dry_run:
                conn.commit()
    finally:
        engine.dispose()

    print()
    if args.dry_run:
        print("[DRY-RUN] 未写库。确认无误后去掉 --dry-run 重新执行。")
    else:
        print("[OK] 客户端菜单结构重组完成")


if __name__ == "__main__":
    main()
