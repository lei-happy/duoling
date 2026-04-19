"""
为 sys_tenant 表新增 menu_version 字段（菜单版本戳）

用途：
    用于"运营后台修改客户版本授权后客户端菜单不刷新"问题的修复。
    每次 assign_product / remove_product 时递增此字段，
    客户端调用 GET /api/client/auth/menu-version 与本地缓存对比，
    不一致则强制重新拉取 /auth/user-info。

用法：
    python backend/scripts/fix/add_tenant_menu_version.py
    python backend/scripts/fix/add_tenant_menu_version.py --dry-run
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect
from app.core.config import get_settings


def column_exists(engine, table: str, column: str) -> bool:
    insp = sa_inspect(engine)
    cols = {c["name"] for c in insp.get_columns(table)}
    return column in cols


def add_column(dry_run: bool = False) -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    table = "sys_tenant"
    column = "menu_version"

    if column_exists(engine, table, column):
        print(f"[SKIP] {table}.{column} 已存在，无需新增")
        engine.dispose()
        return

    ddl = (
        f"ALTER TABLE `{table}` "
        f"ADD COLUMN `{column}` BIGINT NOT NULL DEFAULT 0 "
        f"COMMENT '菜单版本戳：版本授权变更时递增，前端据此判断是否需重新拉取菜单'"
    )

    if dry_run:
        print(f"[DRY-RUN] 将执行：\n  {ddl}")
        engine.dispose()
        return

    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()
    print(f"[OK] 已新增字段 {table}.{column}")
    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="仅预览不执行 DDL")
    args = parser.parse_args()

    add_column(dry_run=args.dry_run)
    print("\n完成！")
