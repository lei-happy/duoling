"""
把运力宝(ylb)相关、历史上以「未实现占位」身份建成 visible=0 的 client 菜单置为可见。

背景：
    `证照监控`(feature_code=fleet_compliance) 菜单早期作为占位以 visible=0 入库。
    运力宝上线后该功能已实现，client_menu.json 快照已是 visible=1，但
    seed_client_menus 为 preserve-ui 模式（不覆盖既有菜单的 icon/排序/可见性），
    因此存量环境的该菜单仍是 visible=0，客户端侧边栏不显示。

    本脚本对存量环境做一次性修正：把这些功能菜单 visible 置 1，并 bump 所有租户
    menu_version，触发在线客户端重新拉取菜单。幂等，可重复执行。

执行（在 backend 目录 / 容器内）：
    python -m scripts.fix.show_ylb_menus
    python -m scripts.fix.show_ylb_menus --dry-run

生产：bash deploy.sh update 之后执行一次，或在 console 后台手动开启菜单显示。
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import bindparam, create_engine, text

from app.core.config import get_settings

# 需要从占位 visible=0 翻转为可见的功能菜单 feature_code
TARGET_FEATURE_CODES = ["fleet_compliance"]


def fix(dry_run: bool = False) -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT id, menu_name, feature_code, visible FROM sys_menu "
                "WHERE app_type = 'client' AND is_deleted = 0 "
                "AND feature_code IN :codes AND visible <> 1"
            ).bindparams(bindparam("codes", expanding=True)),
            {"codes": TARGET_FEATURE_CODES},
        ).fetchall()

        if not rows:
            print("[OK] 无需修正：目标功能菜单均已可见")
            engine.dispose()
            return

        for r in rows:
            print(f"[FIX ] id={r[0]} {r[1]} (feature={r[2]}) visible {r[3]} -> 1")

        if dry_run:
            print(f"\n[DRY-RUN] 共需置可见 {len(rows)} 条菜单，未提交事务")
            engine.dispose()
            return

        conn.execute(
            text(
                "UPDATE sys_menu SET visible = 1 "
                "WHERE app_type = 'client' AND is_deleted = 0 "
                "AND feature_code IN :codes AND visible <> 1"
            ).bindparams(bindparam("codes", expanding=True)),
            {"codes": TARGET_FEATURE_CODES},
        )
        bump = (
            conn.execute(
                text(
                    "UPDATE sys_tenant SET menu_version = menu_version + 1 "
                    "WHERE is_deleted = 0"
                )
            ).rowcount
            or 0
        )
        conn.commit()
        print(f"\n[OK] 已置可见 {len(rows)} 条菜单")
        print(f"[OK] 已递增 {bump} 个租户 menu_version，客户端将自动刷新菜单")

    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="把运力宝功能菜单(证照监控)从占位 visible=0 置为可见"
    )
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写库")
    args = parser.parse_args()
    fix(dry_run=args.dry_run)
