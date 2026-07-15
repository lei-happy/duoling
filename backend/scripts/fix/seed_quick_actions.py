"""
将原前端硬编码的快捷操作注册表回填到 sys_menu.quick_action（一次性）

背景：
    快捷操作目录由「前端硬编码注册表」迁移为「Console 客户端菜单可配置」后，
    原有 9 个默认快捷操作需要在 sys_menu(app_type='client') 上按 menu_code 标记，
    否则改造后租户端首页快捷区为空。

    图标(icon)留空，待运营在 Console 上传专属图标；前端未配图标时用占位图标兜底。
    仅对 quick_action 仍为 NULL 的菜单写入，避免覆盖运营已有配置。

执行：
    python backend/scripts/fix/seed_quick_actions.py            # 真实执行
    python backend/scripts/fix/seed_quick_actions.py --dry-run  # 仅预览
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text

from app.core.config import get_settings


# menu_code -> quick_action 配置（对齐原 quick-action-registry.ts）
DEFAULTS: Dict[str, Dict[str, Any]] = {
    "business:waybill:add": {
        "name": "新建运单", "color": "#69c0ff", "group": "运营调度",
        "link": "/operation/waybill?action=create", "sort": 10, "default": True,
    },
    "operation:task:add": {
        "name": "新建配载", "color": "#b37feb", "group": "运营调度",
        "link": "/operation/task-create", "sort": 20, "default": True,
    },
    "business:waybill:list": {
        "name": "运单管理", "color": "#5cdbd3", "group": "运营调度",
        "link": "/operation/waybill", "sort": 30, "default": True,
    },
    "operation:task:list": {
        "name": "调度任务", "color": "#ff9c6e", "group": "运营调度",
        "link": "/operation/task", "sort": 40, "default": True,
    },
    "partner:customer:list": {
        "name": "客户管理", "color": "#95de64", "group": "客商中心",
        "link": "/partner/customer", "sort": 50, "default": True,
    },
    "capacity:self_capacity:vehicle:list": {
        "name": "车辆管理", "color": "#ffc069", "group": "运力中心",
        "link": "/capacity/self-capacity/vehicle", "sort": 60, "default": True,
    },
    "billing:contract:list": {
        "name": "运价合同", "color": "#ffd666", "group": "计费中心",
        "link": "/billing/contract", "sort": 70, "default": False,
    },
    "partner:carrier:list": {
        "name": "承运商管理", "color": "#ff85c0", "group": "客商中心",
        "link": "/partner/carrier", "sort": 80, "default": False,
    },
    "capacity:social_capacity:list": {
        "name": "社会运力", "color": "#597ef7", "group": "运力中心",
        "link": "/capacity/social-capacity/list", "sort": 90, "default": False,
    },
}


def seed(dry_run: bool = False) -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    affected_total = 0
    with engine.connect() as conn:
        for menu_code, cfg in DEFAULTS.items():
            cfg = {"icon": None, **cfg}
            cnt = conn.execute(
                text(
                    "SELECT COUNT(*) FROM sys_menu "
                    "WHERE menu_code = :code AND app_type = 'client' "
                    "AND is_deleted = 0 AND quick_action IS NULL"
                ),
                {"code": menu_code},
            ).scalar() or 0
            if cnt == 0:
                print(f"[SKIP] {menu_code:<40s} 未找到或已配置")
                continue
            print(f"[SEED] {menu_code:<40s} 影响 {cnt} 条")
            affected_total += cnt
            if dry_run:
                continue
            conn.execute(
                text(
                    "UPDATE sys_menu SET quick_action = :qa "
                    "WHERE menu_code = :code AND app_type = 'client' "
                    "AND is_deleted = 0 AND quick_action IS NULL"
                ),
                {"qa": json.dumps(cfg, ensure_ascii=False), "code": menu_code},
            )

        if affected_total == 0:
            print("\n[OK] 无需回填")
            engine.dispose()
            return

        if dry_run:
            print(f"\n[DRY-RUN] 共需回填 {affected_total} 条，未提交事务")
            engine.dispose()
            return

        bump = conn.execute(
            text(
                "UPDATE sys_tenant SET menu_version = menu_version + 1 "
                "WHERE is_deleted = 0"
            )
        ).rowcount or 0
        conn.commit()
        print(f"\n[OK] 回填完成，共更新 {affected_total} 条菜单")
        print(f"[OK] 已递增 {bump} 个租户 menu_version，客户端将自动刷新")

    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="回填 sys_menu.quick_action 默认快捷操作配置"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="仅预览将要写入的记录数"
    )
    args = parser.parse_args()
    seed(dry_run=args.dry_run)
