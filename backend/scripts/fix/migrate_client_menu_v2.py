"""
客户端菜单 v1.0 → v2.0 迁移脚本

对应：项目文档/02.需求文档/02.企业端/01.客户端菜单架构重构设计.md (v2.0)

执行内容（按顺序）：
  0. 调用 fix_client_menu_v2.run_fix() 清理 ID 冲突 + 重复 + 自引用
       - 物理删除占位的旧 platform 记录 (260/261/262)
       - 物理删除 v1.0 残留重复行 (267/268/269)
       - 拆 264 自引用、把 263-266 临时置为孤儿（seed 会修回正确 parent）
  1. 软删除 v2.0 已废弃的容器型菜单（其子菜单已迁出到新的一级菜单）
  2. 调用 seed_client_menus.py --force-all 完成菜单结构同步
       - 首次 v2 切换需要重排 sort_order/visible/icon，因此用 --force-all
  3. 调用 seed_product_features.py 完成 feature 与版本关联同步

新版 seed_client_menus.py 已支持基于 _seed_id（JSON 中的 id）匹配老记录，
所以重命名 / 路径变更 / 父级迁移等均可被原地 UPDATE，不会产生重复行；
并且会在遇到 ID 主键冲突时直接报错，不会再静默失败。

用法：
    python backend/scripts/fix/migrate_client_menu_v2.py [--dry-run]
    python backend/scripts/fix/migrate_client_menu_v2.py --skip-fix
    python backend/scripts/fix/migrate_client_menu_v2.py --skip-seed
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text

from app.core.config import get_settings
from fix_client_menu_v2 import run_fix as run_data_fix


# 这些一级容器在 v2.0 中已被合并/拆分，子项已迁移到新的一级菜单
DEPRECATED_CLIENT_MENUS = [
    {"id": 177, "name": "资源管理", "reason": "拆分到 运力中心 / 计费中心"},
    {"id": 200, "name": "数据中心", "reason": "重命名为 数据洞察（id=215）"},
    {"id": 208, "name": "基础数据", "reason": "降级为 企业管理 二级菜单容器（id=320）"},
]


def soft_delete_legacy(engine, dry_run: bool = False):
    """软删除已废弃的客户端一级容器"""
    with engine.connect() as conn:
        for item in DEPRECATED_CLIENT_MENUS:
            row = conn.execute(
                text(
                    "SELECT id, menu_name, is_deleted FROM sys_menu "
                    "WHERE id = :id AND app_type = 'client'"
                ),
                {"id": item["id"]},
            ).fetchone()
            if not row:
                print(f"  [SKIP] id={item['id']} 不存在")
                continue
            if int(row.is_deleted) == 1:
                print(f"  [SKIP] id={item['id']} ({row.menu_name}) 已是软删除状态")
                continue
            print(
                f"  [{'DRY-RUN' if dry_run else 'SOFT-DEL'}] id={item['id']} {row.menu_name} "
                f"→ {item['reason']}"
            )
            if not dry_run:
                conn.execute(
                    text(
                        "UPDATE sys_menu SET is_deleted = 1, "
                        "updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                    ),
                    {"id": item["id"]},
                )
        if not dry_run:
            conn.commit()


def main():
    parser = argparse.ArgumentParser(description="客户端菜单 v1.0 → v2.0 迁移")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅打印将执行的操作，不写库",
    )
    parser.add_argument(
        "--skip-fix", action="store_true",
        help="跳过第零步（数据修复 fix_client_menu_v2）",
    )
    parser.add_argument(
        "--skip-seed", action="store_true",
        help="只执行修复+软删除，不调用后续 seed 脚本",
    )
    args = parser.parse_args()

    settings = get_settings()
    db_name = settings.platform_database_name
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{db_name}?charset=utf8mb4"
    )
    engine = create_engine(url)

    if not args.skip_fix:
        print("=" * 60)
        print("第零步：清理 v1.0 → v2.0 历史脏数据 (fix_client_menu_v2)")
        print("=" * 60)
        run_data_fix(dry_run=args.dry_run, soft_delete_orphans=False)
    else:
        print("[INFO] --skip-fix 已指定，跳过 fix_client_menu_v2")

    print()
    print("=" * 60)
    print("第一步：软删除 v2.0 已废弃的客户端一级容器")
    print("=" * 60)
    soft_delete_legacy(engine, dry_run=args.dry_run)
    engine.dispose()

    if args.skip_seed:
        print("\n[INFO] --skip-seed 已指定，跳过 seed 脚本调用")
        return
    if args.dry_run:
        print("\n[INFO] --dry-run 已指定，跳过 seed 脚本调用")
        return

    here = os.path.dirname(__file__)
    seed_dir = os.path.normpath(os.path.join(here, "..", "seed"))

    print("\n" + "=" * 60)
    print("第二步：同步 v2.0 菜单结构（seed_client_menus.py --force-all）")
    print("  说明：首次 v2 切换需要一次性重排 sort_order/visible/icon，")
    print("        故使用 --force-all。后续日常 seed 仍可用默认 preserve-ui。")
    print("=" * 60)
    subprocess.check_call(
        [
            sys.executable,
            os.path.join(seed_dir, "seed_client_menus.py"),
            "--force-all",
        ]
    )

    print("\n" + "=" * 60)
    print("第三步：同步 v2.0 功能清单与版本关联（seed_product_features.py）")
    print("=" * 60)
    subprocess.check_call(
        [sys.executable, os.path.join(seed_dir, "seed_product_features.py")]
    )

    print("\nv2.0 客户端菜单迁移完成！")
    print("提示：刷新浏览器、重启前端 dev server 后再验证菜单效果。")


if __name__ == "__main__":
    main()
