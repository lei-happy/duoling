"""
客户端菜单 v2.0 数据修复脚本

针对历史已运行 v1.0 → v2.0 迁移的环境，修复以下脏数据：

  1. 物理删除被旧 platform 菜单占用的 ID（260/261/262）
     —— 这些 ID 在 v2.0 中分配给了 client 端的 运力中心/运力调配/查询，
        但生产 DB 它们已是 is_deleted=1 的 platform 菜单（用户管理/司机列表/平台运力），
        导致 seed_client_menus.py INSERT 时主键冲突而静默失败。

  2. 物理删除 v1.0 残留的运力子菜单重复行（267/268/269）
     —— 与 263/264/265/266 重名重 menu_code，且 parent_id 错乱。

  3. 拆掉 264 自引用、把 263-266 临时置为孤儿状态
     —— 后续 seed_client_menus.py 通过 _seed_id 命中并 UPDATE 回正确 parent。

  4. 打印剩余孤儿 client 菜单（parent_id != 0 且不在 active 集合），
     可加 --soft-delete-orphans 一并软删除。

幂等：可重复执行，已处理过的不会再动。

用法：
    python backend/scripts/fix/fix_client_menu_v2.py --dry-run            # 预览
    python backend/scripts/fix/fix_client_menu_v2.py                      # 执行
    python backend/scripts/fix/fix_client_menu_v2.py --soft-delete-orphans  # 顺带软删孤儿
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text

from app.core.config import get_settings


# v2.0 中分配给 client 但生产 DB 被旧 platform 占用的 ID
PLATFORM_PLACEHOLDER_IDS = [260, 261, 262]

# v1.0 残留的重复运力子菜单（与 263-266 重名重 code）
LEGACY_DUP_CLIENT_IDS = [267, 268, 269]

# v2.0 中 _seed_id 命中后会 UPDATE 回正确 parent 的菜单
# 但当前可能存在 parent_id 错乱（含 264 自引用）
# 临时把它们置为 parent_id=0、visible=0、sort=9999，后续 seed 会改回
CAPACITY_LEAF_IDS = [263, 264, 265, 266]


def _build_engine():
    settings = get_settings()
    return create_engine(settings.platform_db_url_sync)


def step1_delete_platform_placeholders(conn, dry_run: bool):
    print()
    print("=" * 60)
    print("Step 1: 物理删除占用 v2.0 client ID 的旧 platform 记录")
    print("=" * 60)
    for mid in PLATFORM_PLACEHOLDER_IDS:
        row = conn.execute(
            text(
                "SELECT id, menu_name, app_type, is_deleted "
                "FROM sys_menu WHERE id = :id"
            ),
            {"id": mid},
        ).fetchone()
        if not row:
            print(f"  [SKIP] id={mid} 不存在")
            continue
        if row.app_type != "platform":
            print(
                f"  [SKIP] id={mid} ({row.menu_name}) 不是 platform 菜单 "
                f"(app_type={row.app_type})，跳过物理删除"
            )
            continue
        if int(row.is_deleted) != 1:
            print(
                f"  [WARN] id={mid} ({row.menu_name}) 是 platform 菜单但 is_deleted=0，"
                "请人工确认后再处理"
            )
            continue

        # 双重保险：检查是否有未软删的 platform 子菜单依赖
        child = conn.execute(
            text(
                "SELECT COUNT(*) FROM sys_menu "
                "WHERE parent_id = :pid AND is_deleted = 0"
            ),
            {"pid": mid},
        ).scalar()
        if child and int(child) > 0:
            print(
                f"  [WARN] id={mid} ({row.menu_name}) 仍有 {child} 个未删子菜单，跳过"
            )
            continue

        prefix = "DRY-RUN" if dry_run else "DELETE"
        print(f"  [{prefix}] DELETE id={mid} {row.menu_name} (platform, is_deleted=1)")
        if not dry_run:
            conn.execute(
                text("DELETE FROM sys_menu WHERE id = :id"),
                {"id": mid},
            )


def _table_exists(conn, table_name: str) -> bool:
    """检测当前数据库下指定表是否存在"""
    return bool(
        conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name = :t"
            ),
            {"t": table_name},
        ).scalar()
    )


def step2_delete_legacy_duplicates(conn, dry_run: bool):
    print()
    print("=" * 60)
    print("Step 2: 物理删除 v1.0 残留的重复运力子菜单 (267/268/269)")
    print("=" * 60)
    role_menu_exists = _table_exists(conn, "sys_role_menu")
    if not role_menu_exists:
        print("  [INFO] sys_role_menu 表不存在，跳过角色-菜单关联清理")

    for mid in LEGACY_DUP_CLIENT_IDS:
        row = conn.execute(
            text(
                "SELECT id, menu_name, menu_code, app_type FROM sys_menu "
                "WHERE id = :id"
            ),
            {"id": mid},
        ).fetchone()
        if not row:
            print(f"  [SKIP] id={mid} 不存在")
            continue
        if row.app_type != "client":
            print(
                f"  [SKIP] id={mid} ({row.menu_name}) 不是 client 菜单，跳过"
            )
            continue
        prefix = "DRY-RUN" if dry_run else "DELETE"
        print(
            f"  [{prefix}] DELETE id={mid} {row.menu_name} "
            f"(menu_code={row.menu_code})"
        )
        if not dry_run:
            # 同步清理可能挂在它上面的角色-菜单关联（表名以模型为准: sys_role_menu）
            if role_menu_exists:
                conn.execute(
                    text("DELETE FROM sys_role_menu WHERE menu_id = :id"),
                    {"id": mid},
                )
            conn.execute(
                text("DELETE FROM sys_menu WHERE id = :id"),
                {"id": mid},
            )


def step3_reset_capacity_leaves(conn, dry_run: bool):
    print()
    print("=" * 60)
    print("Step 3: 拆 264 自引用，把 263-266 临时置为孤儿（seed 会修复）")
    print("=" * 60)
    for mid in CAPACITY_LEAF_IDS:
        row = conn.execute(
            text(
                "SELECT id, menu_name, parent_id, app_type, is_deleted "
                "FROM sys_menu WHERE id = :id"
            ),
            {"id": mid},
        ).fetchone()
        if not row:
            print(f"  [SKIP] id={mid} 不存在")
            continue
        if row.app_type != "client":
            print(f"  [SKIP] id={mid} 不是 client 菜单")
            continue
        if int(row.is_deleted) == 1:
            print(f"  [SKIP] id={mid} ({row.menu_name}) 已软删，无需重置")
            continue
        prefix = "DRY-RUN" if dry_run else "UPDATE"
        print(
            f"  [{prefix}] id={mid} {row.menu_name}: parent_id {row.parent_id} -> 0, "
            f"visible -> 0, sort_order -> 9999"
        )
        if not dry_run:
            conn.execute(
                text(
                    "UPDATE sys_menu SET parent_id = 0, visible = 0, "
                    "sort_order = 9999, updated_at = CURRENT_TIMESTAMP "
                    "WHERE id = :id"
                ),
                {"id": mid},
            )


def step4_report_orphans(conn, soft_delete: bool, dry_run: bool):
    print()
    print("=" * 60)
    print("Step 4: 检查孤儿 client 菜单（parent_id 不在 active 集合）")
    print("=" * 60)
    rows = conn.execute(
        text(
            "SELECT id, menu_name, parent_id, path, menu_code "
            "FROM sys_menu WHERE app_type = 'client' AND is_deleted = 0 "
            "ORDER BY id"
        )
    ).fetchall()
    active_ids = {int(r.id) for r in rows}
    orphans = [
        r for r in rows
        if int(r.parent_id) != 0 and int(r.parent_id) not in active_ids
    ]
    if not orphans:
        print("  [OK] 无孤儿菜单")
        return
    print(f"  发现 {len(orphans)} 个孤儿 client 菜单:")
    for r in orphans:
        print(
            f"    id={r.id} {r.menu_name:<14} parent_id={r.parent_id} "
            f"path={r.path} code={r.menu_code}"
        )

    if not soft_delete:
        print()
        print("  [INFO] 如需自动软删，重新执行时加 --soft-delete-orphans")
        return

    prefix = "DRY-RUN" if dry_run else "SOFT-DEL"
    for r in orphans:
        print(f"  [{prefix}] SOFT-DELETE id={r.id} {r.menu_name}")
        if not dry_run:
            conn.execute(
                text(
                    "UPDATE sys_menu SET is_deleted = 1, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                ),
                {"id": r.id},
            )


def run_fix(dry_run: bool = False, soft_delete_orphans: bool = False):
    """供 migrate_client_menu_v2.py 内部调用的入口（不含 argparse）"""
    engine = _build_engine()
    try:
        with engine.connect() as conn:
            step1_delete_platform_placeholders(conn, dry_run)
            step2_delete_legacy_duplicates(conn, dry_run)
            step3_reset_capacity_leaves(conn, dry_run)
            step4_report_orphans(conn, soft_delete_orphans, dry_run)
            if not dry_run:
                conn.commit()
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(
        description="v2.0 客户端菜单数据修复（清理 ID 冲突 + 重复 + 自引用）"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只打印将执行的操作，不写库",
    )
    parser.add_argument(
        "--soft-delete-orphans", action="store_true",
        help="顺带把孤儿 client 菜单一并软删除（默认仅打印）",
    )
    args = parser.parse_args()

    print("v2.0 客户端菜单数据修复脚本")
    print(f"  dry_run = {args.dry_run}")
    print(f"  soft_delete_orphans = {args.soft_delete_orphans}")

    run_fix(dry_run=args.dry_run, soft_delete_orphans=args.soft_delete_orphans)

    print()
    if args.dry_run:
        print("[DRY-RUN] 未写库。确认无误后去掉 --dry-run 重新执行。")
    else:
        print("修复完成！请继续执行: python backend/scripts/fix/migrate_client_menu_v2.py")


if __name__ == "__main__":
    main()
