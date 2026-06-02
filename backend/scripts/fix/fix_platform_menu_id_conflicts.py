"""
平台菜单 ID 冲突预清理（platform_sync sync 前自动调用）

client / platform 共用 sys_menu.id 自增空间。dev 导出的 platform_menu.json 里
新菜单 id（如 812）在生产库可能已被 client 或其它 app_type 的记录占用，
导致 seed_client_menus.py 无法 INSERT，platform_sync 自检仍报「新增 1 条」。

本脚本扫描 platform_menu.json 快照中的 id，清理可安全删除的跨 app_type 墓碑记录
（is_deleted=1 且无未删子节点）。活跃冲突由 seed 脚本 fallback 到自增 id 处理。

用法：
    python -m scripts.fix.fix_platform_menu_id_conflicts
    python -m scripts.fix.fix_platform_menu_id_conflicts --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text

from app.core.config import get_settings

PLATFORM_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1]
    / "platform_sync"
    / "snapshots"
    / "platform_menu.json"
)


def _load_platform_snapshot_ids() -> list[int]:
    if not PLATFORM_SNAPSHOT_PATH.is_file():
        return []
    with PLATFORM_SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
        rows = json.load(f)
    ids: list[int] = []
    for row in rows or []:
        if row.get("app_type") != "platform":
            continue
        if int(row.get("is_deleted", 0)) != 0:
            continue
        rid = row.get("id")
        if isinstance(rid, int):
            ids.append(rid)
    return sorted(set(ids))


def run_fix(*, dry_run: bool = False) -> None:
    snapshot_ids = _load_platform_snapshot_ids()
    if not snapshot_ids:
        print(f"[SKIP] 未找到 platform 快照: {PLATFORM_SNAPSHOT_PATH}")
        return

    engine = create_engine(get_settings().platform_db_url_sync)
    try:
        with engine.connect() as conn:
            placeholders = ",".join(str(i) for i in snapshot_ids)
            rows = conn.execute(
                text(
                    f"SELECT id, menu_name, app_type, is_deleted "
                    f"FROM sys_menu WHERE id IN ({placeholders})"
                )
            ).fetchall()

            if not rows:
                print("[OK] platform 快照 ID 在 DB 中均未被占用")
                return

            deleted = 0
            warned = 0
            for row in rows:
                if row.app_type == "platform" and int(row.is_deleted) == 0:
                    continue
                child_cnt = conn.execute(
                    text(
                        "SELECT COUNT(*) FROM sys_menu "
                        "WHERE parent_id = :pid AND is_deleted = 0"
                    ),
                    {"pid": int(row.id)},
                ).scalar() or 0
                if int(child_cnt) > 0:
                    print(
                        f"  [WARN] id={row.id} ({row.menu_name}, app_type={row.app_type}) "
                        f"仍有 {child_cnt} 个未删子菜单，跳过物理删除"
                    )
                    warned += 1
                    continue

                if int(row.is_deleted) == 1:
                    action = "DRY-DELETE" if dry_run else "DELETE"
                    print(
                        f"  [{action}] id={row.id} {row.menu_name} "
                        f"(app_type={row.app_type}, 释放 platform 快照 ID)"
                    )
                    if not dry_run:
                        conn.execute(
                            text("DELETE FROM sys_menu WHERE id = :id"),
                            {"id": int(row.id)},
                        )
                    deleted += 1
                else:
                    print(
                        f"  [WARN] id={row.id} ({row.menu_name}) 被活跃的 "
                        f"{row.app_type} 菜单占用，seed 将 fallback 到自增 ID"
                    )
                    warned += 1

            if not dry_run and deleted:
                conn.commit()

            print(
                f"[OK] platform 菜单 ID 预清理完成："
                f"删除墓碑 {deleted} 条，需 seed fallback/人工关注 {warned} 条"
            )
    finally:
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="platform 菜单 ID 冲突预清理")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写库")
    args = parser.parse_args()
    run_fix(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
