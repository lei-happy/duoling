"""
修复线上 sys_menu 表中"已废弃 / 拼写不一致"的 feature_code

背景：
    早期版本的 client 菜单使用了与 seed_product_features.py 中 FEATURES 不一致的
    feature_code（典型如 biz_order / resource_customer / regional_data 等），导致
    AuthService._get_user_menus 在 client 端用 feature_code IN (...) 过滤时把它们
    永远剔除。客户端因此看不到这些菜单，体感就是「在版本里勾选了功能但客户端不显示」。

    本脚本对线上环境一次性把这些脏值改成有效值（或置 NULL，让目录类菜单对所有
    版本都可见），并把所有租户 menu_version + 1，强制客户端重新拉取菜单。

执行：
    python backend/scripts/fix/fix_stale_feature_codes.py            # 真实执行
    python backend/scripts/fix/fix_stale_feature_codes.py --dry-run  # 仅预览

如新增其他映射，可直接追加到 STALE_MAP。
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text

from app.core.config import get_settings


# ---------------------------------------------------------------------------
# 待修复映射：旧 feature_code -> 新 feature_code（None 表示置 NULL，作为目录菜单）
# ---------------------------------------------------------------------------
STALE_MAP: dict[str, Optional[str]] = {
    # 父级目录类菜单不需要 feature_code，置 NULL 后对所有版本可见
    "resource_manage": None,
    "bi_analytics": None,
    # 与 FEATURES 中的 biz_waybill 对齐
    "biz_order": "biz_waybill",
    # 旧"客户管理"由资源中心迁移到客商中心，归并到 partner_customer
    "resource_customer": "partner_customer",
    # 早期占位的"地区数据"已统一到 basic_data_region
    "regional_data": "basic_data_region",
    # 运力中心模块 v3 重构（migrate_capacity_v3.py）：旧 feature_code -> 新 feature_code
    # 用于 prod 上仍持有旧 code 的 sys_menu 行做兜底；新菜单已直接写入 v3 code，
    # 但若历史快照恢复或部分行漏改，本映射可补救。
    "capacity_manage": "capacity_center",
    "resource_vehicle": "capacity_self_vehicle",
    "resource_trailer": "capacity_self_trailer",
    "resource_driver": "capacity_self_driver",
    "carrier_external": "capacity_carrier",
    "carrier_social": "capacity_social",
}


def fix(dry_run: bool = False) -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    affected_total = 0
    with engine.connect() as conn:
        for old_code, new_code in STALE_MAP.items():
            row = conn.execute(
                text(
                    "SELECT COUNT(*) FROM sys_menu "
                    "WHERE feature_code = :code "
                    "AND app_type = 'client' AND is_deleted = 0"
                ),
                {"code": old_code},
            ).scalar()
            row = row or 0
            if row == 0:
                print(f"[SKIP] {old_code:>22s}  -> 未发现激活记录")
                continue
            arrow = "NULL" if new_code is None else new_code
            print(f"[FIX ] {old_code:>22s}  -> {arrow:<22s}  影响 {row} 条")
            affected_total += row
            if dry_run:
                continue
            if new_code is None:
                conn.execute(
                    text(
                        "UPDATE sys_menu SET feature_code = NULL "
                        "WHERE feature_code = :code "
                        "AND app_type = 'client' AND is_deleted = 0"
                    ),
                    {"code": old_code},
                )
            else:
                conn.execute(
                    text(
                        "UPDATE sys_menu SET feature_code = :new_code "
                        "WHERE feature_code = :old_code "
                        "AND app_type = 'client' AND is_deleted = 0"
                    ),
                    {"new_code": new_code, "old_code": old_code},
                )

        if affected_total == 0:
            print("\n[OK] 数据库中没有需要修复的脏 feature_code")
            engine.dispose()
            return

        if dry_run:
            print(f"\n[DRY-RUN] 共需要修复 {affected_total} 条记录，未提交事务")
            engine.dispose()
            return

        # 触发所有租户 menu_version + 1，让客户端在路由切换时重新拉菜单
        bump_count = (
            conn.execute(
                text(
                    "UPDATE sys_tenant SET menu_version = menu_version + 1 "
                    "WHERE is_deleted = 0"
                )
            ).rowcount
            or 0
        )
        conn.commit()
        print(f"\n[OK] 修复完成，共更新 {affected_total} 条菜单")
        print(f"[OK] 已递增 {bump_count} 个租户的 menu_version，客户端将自动刷新菜单")

    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="修复 sys_menu 中已废弃的 feature_code，并触发客户端菜单刷新"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="仅预览将要修改的记录数，不真正写库"
    )
    args = parser.parse_args()
    fix(dry_run=args.dry_run)
