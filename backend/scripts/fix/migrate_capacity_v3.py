"""
运力中心模块 v3 数据迁移脚本（一次性，幂等）

对应：
  - 项目计划 `运力中心模块重组_972a88c6.plan.md`
  - 前端目录 `frontend/client/src/views/capacity/{self_capacity,carrier_capacity,social_capacity}`

执行内容（按顺序，每步幂等）：
  1. 写入/修正运力 v3 容器与页面菜单的 menu_code / feature_code / parent_id（13 条）
  2. 创建 v3 按钮权限菜单（16 条 menu_type=1，按 menu_code 幂等 upsert）
  3. 把 sys_role_menu 中指向旧按钮/容器的 menu_id 迁移到新菜单 id
  4. 软删 21 条旧菜单（5 容器 + 16 按钮）
  5. 在 sys_product_feature 中插入 13 个新 feature_code，并把 6 个旧 code 设 is_deleted=1
  6. 重建 sys_version_feature 中 lite/standard/pro 三档的运力相关条目（按 §1.5 方案）
  7. 把所有租户的 sys_tenant.menu_version + 1，强制客户端重新拉菜单

用法：
    python backend/scripts/fix/migrate_capacity_v3.py            # 真实执行
    python backend/scripts/fix/migrate_capacity_v3.py --dry-run  # 仅预览，不写库
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Connection

from app.core.config import get_settings


# ---------------------------------------------------------------------------
# §1.1 / §1.2  v3 菜单事实源
# ---------------------------------------------------------------------------

# 一级容器：260 (运力中心) 仍保留，仅替换 feature_code
ROOT_MENU_ID = 260
ROOT_NEW_MENU_CODE = "capacity"
ROOT_NEW_FEATURE_CODE = "capacity_center"

# 已存在的 v3 容器/页面（13 条）：补全 menu_code / feature_code / parent_id
# parent_id 仅在与目标值不一致时才更新，避免破坏前端已配置的 sort_order 等 UI 字段。
V3_EXISTING_MENUS: list[dict] = [
    # 运力中心 一级容器
    {
        "id": 260, "menu_code": "capacity", "feature_code": "capacity_center",
        "parent_id": 0, "menu_name": "运力中心",
    },
    # 自有运力（容器）
    {
        "id": 338, "menu_code": "capacity:self_capacity", "feature_code": "capacity_self",
        "parent_id": 260, "menu_name": "自有运力",
    },
    {
        "id": 339, "menu_code": "capacity:self_capacity:list", "feature_code": "capacity_self_list",
        "parent_id": 338, "menu_name": "运力列表",
    },
    {
        "id": 342, "menu_code": "capacity:self_capacity:driver", "feature_code": "capacity_self_driver",
        "parent_id": 338, "menu_name": "驾驶员管理",
    },
    {
        "id": 340, "menu_code": "capacity:self_capacity:vehicle", "feature_code": "capacity_self_vehicle",
        "parent_id": 338, "menu_name": "车辆管理",
    },
    {
        "id": 341, "menu_code": "capacity:self_capacity:trailer", "feature_code": "capacity_self_trailer",
        "parent_id": 338, "menu_name": "挂车管理",
    },
    {
        "id": 345, "menu_code": "capacity:self_capacity:log", "feature_code": "capacity_self_log",
        "parent_id": 338, "menu_name": "变更记录",
    },
    # 承运商运力
    {
        "id": 303, "menu_code": "capacity:carrier_capacity", "feature_code": "capacity_carrier",
        "parent_id": 260, "menu_name": "承运商运力",
    },
    {
        "id": 343, "menu_code": "capacity:carrier_capacity:list", "feature_code": "capacity_carrier_list",
        "parent_id": 303, "menu_name": "运力列表",
    },
    {
        "id": 346, "menu_code": "capacity:carrier_capacity:approval", "feature_code": "capacity_carrier_approval",
        "parent_id": 303, "menu_name": "运力审批",
    },
    # 社会运力池
    {
        "id": 304, "menu_code": "capacity:social_capacity", "feature_code": "capacity_social",
        "parent_id": 260, "menu_name": "社会运力池",
    },
    {
        "id": 344, "menu_code": "capacity:social_capacity:list", "feature_code": "capacity_social_list",
        "parent_id": 304, "menu_name": "运力列表",
    },
    {
        "id": 347, "menu_code": "capacity:social_capacity:approval", "feature_code": "capacity_social_approval",
        "parent_id": 304, "menu_name": "运力审批",
    },
]


# 16 条新按钮权限：(parent_id, menu_code, feature_code, menu_name, sort_order)
V3_NEW_BUTTONS: list[dict] = [
    # 自有运力 - 列表（339）
    {"parent_id": 339, "menu_code": "capacity:self_capacity:list:list",
     "feature_code": "capacity_self_list", "menu_name": "查询", "sort_order": 0},
    {"parent_id": 339, "menu_code": "capacity:self_capacity:list:bind",
     "feature_code": "capacity_self_list", "menu_name": "上车", "sort_order": 1},
    {"parent_id": 339, "menu_code": "capacity:self_capacity:list:unbind",
     "feature_code": "capacity_self_list", "menu_name": "下车", "sort_order": 2},
    # 自有运力 - 车辆（340）
    {"parent_id": 340, "menu_code": "capacity:self_capacity:vehicle:list",
     "feature_code": "capacity_self_vehicle", "menu_name": "查询", "sort_order": 0},
    {"parent_id": 340, "menu_code": "capacity:self_capacity:vehicle:add",
     "feature_code": "capacity_self_vehicle", "menu_name": "新增", "sort_order": 1},
    {"parent_id": 340, "menu_code": "capacity:self_capacity:vehicle:edit",
     "feature_code": "capacity_self_vehicle", "menu_name": "编辑", "sort_order": 2},
    {"parent_id": 340, "menu_code": "capacity:self_capacity:vehicle:delete",
     "feature_code": "capacity_self_vehicle", "menu_name": "删除", "sort_order": 3},
    # 自有运力 - 挂车（341）
    {"parent_id": 341, "menu_code": "capacity:self_capacity:trailer:list",
     "feature_code": "capacity_self_trailer", "menu_name": "查询", "sort_order": 0},
    {"parent_id": 341, "menu_code": "capacity:self_capacity:trailer:add",
     "feature_code": "capacity_self_trailer", "menu_name": "新增", "sort_order": 1},
    {"parent_id": 341, "menu_code": "capacity:self_capacity:trailer:edit",
     "feature_code": "capacity_self_trailer", "menu_name": "编辑", "sort_order": 2},
    {"parent_id": 341, "menu_code": "capacity:self_capacity:trailer:delete",
     "feature_code": "capacity_self_trailer", "menu_name": "删除", "sort_order": 3},
    # 自有运力 - 驾驶员（342）
    {"parent_id": 342, "menu_code": "capacity:self_capacity:driver:list",
     "feature_code": "capacity_self_driver", "menu_name": "查询", "sort_order": 0},
    {"parent_id": 342, "menu_code": "capacity:self_capacity:driver:add",
     "feature_code": "capacity_self_driver", "menu_name": "新增", "sort_order": 1},
    {"parent_id": 342, "menu_code": "capacity:self_capacity:driver:edit",
     "feature_code": "capacity_self_driver", "menu_name": "编辑", "sort_order": 2},
    {"parent_id": 342, "menu_code": "capacity:self_capacity:driver:delete",
     "feature_code": "capacity_self_driver", "menu_name": "删除", "sort_order": 3},
    # 自有运力 - 变更记录（345）
    {"parent_id": 345, "menu_code": "capacity:self_capacity:log:list",
     "feature_code": "capacity_self_log", "menu_name": "查询", "sort_order": 0},
]


# §1.2 旧→新 menu_code 映射（用于 sys_role_menu 迁移）
# key 为旧 menu_id，value 为新按钮的 menu_code（新菜单插入后通过 menu_code 反查 id）
LEGACY_BUTTON_MAP: dict[int, str] = {
    # 旧资源-车辆按钮 178/179-182
    178: "capacity:self_capacity:vehicle:list",
    179: "capacity:self_capacity:vehicle:list",
    180: "capacity:self_capacity:vehicle:add",
    181: "capacity:self_capacity:vehicle:edit",
    182: "capacity:self_capacity:vehicle:delete",
    # 旧资源-挂车按钮 183/184-187
    183: "capacity:self_capacity:trailer:list",
    184: "capacity:self_capacity:trailer:list",
    185: "capacity:self_capacity:trailer:add",
    186: "capacity:self_capacity:trailer:edit",
    187: "capacity:self_capacity:trailer:delete",
    # 旧资源-驾驶员按钮 188/255-258
    188: "capacity:self_capacity:driver:list",
    255: "capacity:self_capacity:driver:list",
    256: "capacity:self_capacity:driver:add",
    257: "capacity:self_capacity:driver:edit",
    258: "capacity:self_capacity:driver:delete",
    # 旧运力列表 261/262-264
    261: "capacity:self_capacity:list:list",
    262: "capacity:self_capacity:list:list",
    263: "capacity:self_capacity:list:bind",
    264: "capacity:self_capacity:list:unbind",
    # 旧变更记录 265/266
    265: "capacity:self_capacity:log:list",
    266: "capacity:self_capacity:log:list",
}


# §1.3 待软删的旧菜单（21 条 = 5 容器 + 16 按钮）
LEGACY_MENU_IDS: list[int] = [
    178, 179, 180, 181, 182,
    183, 184, 185, 186, 187,
    188, 255, 256, 257, 258,
    261, 262, 263, 264,
    265, 266,
]


# §1.4 待废弃的 feature_code（6 个）
LEGACY_FEATURE_CODES: list[str] = [
    "capacity_manage",
    "resource_vehicle",
    "resource_trailer",
    "resource_driver",
    "carrier_external",
    "carrier_social",
]


# §1.4 / §4.1 13 个新 feature_code 的元数据
# 字段对齐 sys_product_feature(feature_code, feature_name, module, sort_order, status, required_tables)
NEW_FEATURES: list[dict] = [
    {"feature_code": "capacity_center", "feature_name": "运力中心",
     "module": "capacity", "sort_order": 40, "required_tables": None},
    {"feature_code": "capacity_self", "feature_name": "自有运力",
     "module": "capacity", "sort_order": 41, "required_tables": None},
    {"feature_code": "capacity_self_list", "feature_name": "自有运力-运力列表",
     "module": "capacity", "sort_order": 42,
     "required_tables": ["biz_capacity"]},
    {"feature_code": "capacity_self_driver", "feature_name": "自有运力-驾驶员管理",
     "module": "capacity", "sort_order": 43,
     "required_tables": [
         "biz_driver", "biz_driver_license", "biz_driver_operation",
         "biz_driver_account", "biz_driver_route",
     ]},
    {"feature_code": "capacity_self_vehicle", "feature_name": "自有运力-车辆管理",
     "module": "capacity", "sort_order": 44,
     "required_tables": ["biz_vehicle", "biz_vehicle_ext"]},
    {"feature_code": "capacity_self_trailer", "feature_name": "自有运力-挂车管理",
     "module": "capacity", "sort_order": 45,
     "required_tables": ["biz_trailer", "biz_trailer_ext"]},
    {"feature_code": "capacity_self_log", "feature_name": "自有运力-变更记录",
     "module": "capacity", "sort_order": 46,
     "required_tables": ["biz_capacity_log"]},
    {"feature_code": "capacity_carrier", "feature_name": "承运商运力",
     "module": "capacity", "sort_order": 47, "required_tables": None},
    {"feature_code": "capacity_carrier_list", "feature_name": "承运商运力-运力列表",
     "module": "capacity", "sort_order": 48, "required_tables": None},
    {"feature_code": "capacity_carrier_approval", "feature_name": "承运商运力-运力审批",
     "module": "capacity", "sort_order": 49, "required_tables": None},
    {"feature_code": "capacity_social", "feature_name": "社会运力池",
     "module": "capacity", "sort_order": 50, "required_tables": None},
    {"feature_code": "capacity_social_list", "feature_name": "社会运力池-运力列表",
     "module": "capacity", "sort_order": 51, "required_tables": None},
    {"feature_code": "capacity_social_approval", "feature_name": "社会运力池-运力审批",
     "module": "capacity", "sort_order": 52, "required_tables": None},
]


# §1.5 三个版本的目标 feature_code 集合（仅运力相关，其他保持原样）
LITE_NEW = [
    "capacity_center", "capacity_self",
    "capacity_self_list", "capacity_self_driver", "capacity_self_vehicle",
    "capacity_self_trailer", "capacity_self_log",
]
STANDARD_PRO_NEW = LITE_NEW + [
    "capacity_carrier", "capacity_carrier_list", "capacity_carrier_approval",
    "capacity_social", "capacity_social_list", "capacity_social_approval",
]
VERSION_TARGET: dict[str, list[str]] = {
    "lite": LITE_NEW,
    "standard": STANDARD_PRO_NEW,
    "pro": STANDARD_PRO_NEW,
}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _build_engine():
    settings = get_settings()
    return create_engine(settings.platform_db_url_sync)


def _exec(conn: Connection, sql: str, params: Optional[dict] = None, dry_run: bool = False):
    """根据 dry_run 决定是否真正执行写库语句。读语句请直接 conn.execute。"""
    if dry_run:
        return None
    return conn.execute(text(sql), params or {})


# ---------------------------------------------------------------------------
# Step 1: 修正现有 v3 菜单的 menu_code / feature_code / parent_id
# ---------------------------------------------------------------------------

def step1_update_v3_menus(conn: Connection, dry_run: bool):
    print()
    print("=" * 60)
    print("Step 1: 写入/修正 v3 容器与页面菜单的 menu_code / feature_code / parent_id")
    print("=" * 60)
    updated = 0
    for item in V3_EXISTING_MENUS:
        row = conn.execute(
            text(
                "SELECT id, menu_name, menu_code, feature_code, parent_id, is_deleted "
                "FROM sys_menu WHERE id = :id"
            ),
            {"id": item["id"]},
        ).fetchone()
        if not row:
            print(f"  [SKIP] id={item['id']} ({item['menu_name']}) 不存在，跳过")
            continue

        diffs = []
        if (row.menu_code or "") != item["menu_code"]:
            diffs.append(f"menu_code: {row.menu_code!r} -> {item['menu_code']!r}")
        if (row.feature_code or "") != item["feature_code"]:
            diffs.append(f"feature_code: {row.feature_code!r} -> {item['feature_code']!r}")
        if int(row.parent_id) != item["parent_id"]:
            diffs.append(f"parent_id: {row.parent_id} -> {item['parent_id']}")

        if not diffs:
            print(f"  [SKIP] id={item['id']:<3d} {item['menu_name']:<10s}  已是目标状态")
            continue

        prefix = "DRY-RUN" if dry_run else "UPDATE"
        print(f"  [{prefix}] id={item['id']:<3d} {item['menu_name']:<10s}  " + "; ".join(diffs))
        if not dry_run:
            conn.execute(
                text(
                    "UPDATE sys_menu SET "
                    "  menu_code = :menu_code, feature_code = :feature_code, "
                    "  parent_id = :parent_id, "
                    "  updated_at = CURRENT_TIMESTAMP "
                    "WHERE id = :id"
                ),
                {
                    "id": item["id"],
                    "menu_code": item["menu_code"],
                    "feature_code": item["feature_code"],
                    "parent_id": item["parent_id"],
                },
            )
            updated += 1
    print(f"  -> 共更新 {updated} 条 v3 菜单")


# ---------------------------------------------------------------------------
# Step 2: 创建 v3 按钮权限菜单（幂等：按 menu_code 反查存在则更新）
# ---------------------------------------------------------------------------

def step2_upsert_buttons(conn: Connection, dry_run: bool) -> dict[str, int]:
    print()
    print("=" * 60)
    print("Step 2: upsert v3 按钮权限菜单（16 条 menu_type=1）")
    print("=" * 60)
    code_to_id: dict[str, int] = {}
    inserted = updated = 0
    for btn in V3_NEW_BUTTONS:
        row = conn.execute(
            text(
                "SELECT id, parent_id, menu_name, sort_order, feature_code, is_deleted "
                "FROM sys_menu WHERE menu_code = :code AND app_type = 'client' "
                "ORDER BY id LIMIT 1"
            ),
            {"code": btn["menu_code"]},
        ).fetchone()
        if row:
            code_to_id[btn["menu_code"]] = int(row.id)
            diffs = []
            if int(row.parent_id) != btn["parent_id"]:
                diffs.append(f"parent_id {row.parent_id} -> {btn['parent_id']}")
            if (row.feature_code or "") != btn["feature_code"]:
                diffs.append(
                    f"feature_code {row.feature_code!r} -> {btn['feature_code']!r}"
                )
            if int(row.sort_order) != btn["sort_order"]:
                diffs.append(f"sort_order {row.sort_order} -> {btn['sort_order']}")
            if int(row.is_deleted) == 1:
                diffs.append("is_deleted 1 -> 0")
            if not diffs:
                print(
                    f"  [SKIP] id={int(row.id):<4d} {btn['menu_code']:<48s} 已存在且一致"
                )
                continue
            prefix = "DRY-RUN" if dry_run else "UPDATE"
            print(
                f"  [{prefix}] id={int(row.id):<4d} {btn['menu_code']:<48s} "
                + "; ".join(diffs)
            )
            if not dry_run:
                conn.execute(
                    text(
                        "UPDATE sys_menu SET "
                        "  parent_id = :parent_id, "
                        "  menu_name = :menu_name, "
                        "  sort_order = :sort_order, "
                        "  feature_code = :feature_code, "
                        "  is_deleted = 0, "
                        "  updated_at = CURRENT_TIMESTAMP "
                        "WHERE id = :id"
                    ),
                    {
                        "id": int(row.id),
                        "parent_id": btn["parent_id"],
                        "menu_name": btn["menu_name"],
                        "sort_order": btn["sort_order"],
                        "feature_code": btn["feature_code"],
                    },
                )
                updated += 1
            continue

        prefix = "DRY-RUN" if dry_run else "INSERT"
        print(f"  [{prefix}] INSERT {btn['menu_code']:<48s} parent={btn['parent_id']}")
        if not dry_run:
            conn.execute(
                text(
                    "INSERT INTO sys_menu ("
                    "  parent_id, menu_name, menu_code, menu_type, "
                    "  path, component, icon, sort_order, visible, status, "
                    "  app_type, feature_code, created_at, updated_at, is_deleted"
                    ") VALUES ("
                    "  :parent_id, :menu_name, :menu_code, 1, "
                    "  NULL, NULL, NULL, :sort_order, 1, 1, "
                    "  'client', :feature_code, "
                    "  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0"
                    ")"
                ),
                {
                    "parent_id": btn["parent_id"],
                    "menu_name": btn["menu_name"],
                    "menu_code": btn["menu_code"],
                    "sort_order": btn["sort_order"],
                    "feature_code": btn["feature_code"],
                },
            )
            new_id = int(
                conn.execute(text("SELECT LAST_INSERT_ID()")).scalar() or 0
            )
            code_to_id[btn["menu_code"]] = new_id
            inserted += 1
    print(f"  -> 新增 {inserted} 条，更新 {updated} 条")
    return code_to_id


# ---------------------------------------------------------------------------
# Step 3: 迁移 sys_role_menu 中指向旧菜单的关联到新按钮 id
# ---------------------------------------------------------------------------

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


def step3_migrate_role_menu(
    conn: Connection, code_to_id: dict[str, int], dry_run: bool
):
    print()
    print("=" * 60)
    print("Step 3: 迁移 sys_role_menu 中旧菜单 id -> 新按钮 id")
    print("=" * 60)
    if not _table_exists(conn, "sys_role_menu"):
        print("  [INFO] sys_role_menu 表不存在，跳过")
        return

    migrated = 0
    deleted_dup = 0
    for old_id, new_code in LEGACY_BUTTON_MAP.items():
        new_id = code_to_id.get(new_code)
        if not new_id:
            print(
                f"  [WARN] 旧菜单 id={old_id} 待映射到 menu_code={new_code}，"
                "但新菜单 id 未知（dry-run 且未插入），跳过"
            )
            continue

        # 查询当前角色映射数量
        cnt = (
            conn.execute(
                text(
                    "SELECT COUNT(*) FROM sys_role_menu WHERE menu_id = :old_id"
                ),
                {"old_id": old_id},
            ).scalar()
            or 0
        )
        if cnt == 0:
            continue

        prefix = "DRY-RUN" if dry_run else "MIGRATE"
        print(
            f"  [{prefix}] sys_role_menu.menu_id {old_id:<4d} -> {new_id:<4d} "
            f"({new_code})  影响 {cnt} 行"
        )

        if dry_run:
            continue

        # 已存在 (role_id, new_id) 的角色直接删旧映射避免 UNIQUE/重复
        dup_rows = conn.execute(
            text(
                "SELECT old.role_id FROM sys_role_menu old "
                "JOIN sys_role_menu new ON old.role_id = new.role_id "
                "WHERE old.menu_id = :old_id AND new.menu_id = :new_id"
            ),
            {"old_id": old_id, "new_id": new_id},
        ).fetchall()
        if dup_rows:
            conn.execute(
                text(
                    "DELETE FROM sys_role_menu WHERE menu_id = :old_id "
                    "AND role_id IN ("
                    "  SELECT role_id FROM ("
                    "    SELECT role_id FROM sys_role_menu WHERE menu_id = :new_id"
                    "  ) AS t"
                    ")"
                ),
                {"old_id": old_id, "new_id": new_id},
            )
            deleted_dup += len(dup_rows)
        # 剩余旧映射 UPDATE 到新 id
        result = conn.execute(
            text(
                "UPDATE sys_role_menu SET menu_id = :new_id "
                "WHERE menu_id = :old_id"
            ),
            {"old_id": old_id, "new_id": new_id},
        )
        migrated += result.rowcount or 0

    print(
        f"  -> 迁移角色映射 {migrated} 行；删除冲突重复映射 {deleted_dup} 行"
    )


# ---------------------------------------------------------------------------
# Step 4: 软删 21 条旧菜单
# ---------------------------------------------------------------------------

def step4_soft_delete_legacy_menus(conn: Connection, dry_run: bool):
    print()
    print("=" * 60)
    print(f"Step 4: 软删 {len(LEGACY_MENU_IDS)} 条旧菜单（5 容器 + 16 按钮）")
    print("=" * 60)
    soft_deleted = 0
    for mid in LEGACY_MENU_IDS:
        row = conn.execute(
            text(
                "SELECT id, menu_name, menu_code, app_type, is_deleted "
                "FROM sys_menu WHERE id = :id"
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
        if int(row.is_deleted) == 1:
            print(f"  [SKIP] id={mid} ({row.menu_name}) 已软删")
            continue
        prefix = "DRY-RUN" if dry_run else "SOFT-DEL"
        print(
            f"  [{prefix}] id={mid:<4d} {row.menu_name:<14s}  code={row.menu_code}"
        )
        if not dry_run:
            conn.execute(
                text(
                    "UPDATE sys_menu SET is_deleted = 1, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                ),
                {"id": mid},
            )
            soft_deleted += 1
    print(f"  -> 软删 {soft_deleted} 条旧菜单")


# ---------------------------------------------------------------------------
# Step 5: sys_product_feature upsert + 软删 6 个旧 feature_code
# ---------------------------------------------------------------------------

def step5_upsert_features(conn: Connection, dry_run: bool) -> dict[str, int]:
    print()
    print("=" * 60)
    print("Step 5: upsert 13 个新 feature_code，并软删 6 个旧 feature_code")
    print("=" * 60)
    code_to_id: dict[str, int] = {}
    inserted = updated = soft_deleted = 0

    for feat in NEW_FEATURES:
        row = conn.execute(
            text(
                "SELECT id, feature_name, module, sort_order, status, is_deleted "
                "FROM sys_product_feature WHERE feature_code = :code"
            ),
            {"code": feat["feature_code"]},
        ).fetchone()
        if row:
            code_to_id[feat["feature_code"]] = int(row.id)
            diffs = []
            if int(row.is_deleted) == 1:
                diffs.append("is_deleted 1 -> 0")
            if int(row.status) != 1:
                diffs.append(f"status {row.status} -> 1")
            if (row.feature_name or "") != feat["feature_name"]:
                diffs.append(f"name {row.feature_name!r} -> {feat['feature_name']!r}")
            if (row.module or "") != feat["module"]:
                diffs.append(f"module {row.module!r} -> {feat['module']!r}")
            if int(row.sort_order) != feat["sort_order"]:
                diffs.append(f"sort {row.sort_order} -> {feat['sort_order']}")
            if not diffs:
                print(f"  [SKIP] id={int(row.id):<3d} {feat['feature_code']:<28s} 已存在且一致")
                continue
            prefix = "DRY-RUN" if dry_run else "UPDATE"
            print(
                f"  [{prefix}] id={int(row.id):<3d} {feat['feature_code']:<28s} "
                + "; ".join(diffs)
            )
            if not dry_run:
                conn.execute(
                    text(
                        "UPDATE sys_product_feature SET "
                        "  feature_name = :name, module = :module, "
                        "  sort_order = :sort, required_tables = :req, "
                        "  status = 1, is_deleted = 0, "
                        "  updated_at = CURRENT_TIMESTAMP "
                        "WHERE id = :id"
                    ),
                    {
                        "id": int(row.id),
                        "name": feat["feature_name"],
                        "module": feat["module"],
                        "sort": feat["sort_order"],
                        "req": _json_dumps(feat["required_tables"]),
                    },
                )
                updated += 1
            continue
        prefix = "DRY-RUN" if dry_run else "INSERT"
        print(f"  [{prefix}] INSERT {feat['feature_code']:<28s} ({feat['feature_name']})")
        if not dry_run:
            conn.execute(
                text(
                    "INSERT INTO sys_product_feature ("
                    "  feature_code, feature_name, module, description, "
                    "  required_tables, sort_order, status, "
                    "  created_at, updated_at, is_deleted"
                    ") VALUES ("
                    "  :code, :name, :module, NULL, "
                    "  :req, :sort, 1, "
                    "  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0"
                    ")"
                ),
                {
                    "code": feat["feature_code"],
                    "name": feat["feature_name"],
                    "module": feat["module"],
                    "sort": feat["sort_order"],
                    "req": _json_dumps(feat["required_tables"]),
                },
            )
            new_id = int(
                conn.execute(text("SELECT LAST_INSERT_ID()")).scalar() or 0
            )
            code_to_id[feat["feature_code"]] = new_id
            inserted += 1

    for code in LEGACY_FEATURE_CODES:
        row = conn.execute(
            text(
                "SELECT id, feature_name, is_deleted FROM sys_product_feature "
                "WHERE feature_code = :code"
            ),
            {"code": code},
        ).fetchone()
        if not row:
            print(f"  [SKIP] feature_code={code:<22s} 不存在，无需软删")
            continue
        if int(row.is_deleted) == 1:
            print(f"  [SKIP] feature_code={code:<22s} 已软删")
            continue
        prefix = "DRY-RUN" if dry_run else "SOFT-DEL"
        print(f"  [{prefix}] feature_code={code:<22s} ({row.feature_name})")
        if not dry_run:
            conn.execute(
                text(
                    "UPDATE sys_product_feature SET is_deleted = 1, "
                    "status = 0, updated_at = CURRENT_TIMESTAMP "
                    "WHERE id = :id"
                ),
                {"id": int(row.id)},
            )
            soft_deleted += 1

    print(
        f"  -> feature: 新增 {inserted}，更新 {updated}，软删 {soft_deleted}"
    )
    return code_to_id


def _json_dumps(value):
    if value is None:
        return None
    import json as _json
    return _json.dumps(value, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Step 6: 重建 sys_version_feature 中 lite/standard/pro 的运力相关条目
# ---------------------------------------------------------------------------

def step6_rebuild_version_features(
    conn: Connection, feature_id_map: dict[str, int], dry_run: bool
):
    print()
    print("=" * 60)
    print("Step 6: 重建 sys_version_feature（lite/standard/pro 运力相关）")
    print("=" * 60)

    # 旧 feature_id：从 sys_product_feature 里反查（即使 is_deleted=1 也要拿到 id 用以删除关联）
    legacy_id_map: dict[str, int] = {}
    if LEGACY_FEATURE_CODES:
        stmt = text(
            "SELECT id, feature_code FROM sys_product_feature "
            "WHERE feature_code IN :codes"
        ).bindparams(bindparam("codes", expanding=True))
        rows = conn.execute(stmt, {"codes": list(LEGACY_FEATURE_CODES)}).fetchall()
        for r in rows:
            legacy_id_map[str(r.feature_code)] = int(r.id)

    # 补齐 dry-run 缺失的新 feature_id（dry-run 没真正插入的情况下，反查可能拿不到）
    for code in {c for codes in VERSION_TARGET.values() for c in codes}:
        if code in feature_id_map:
            continue
        row = conn.execute(
            text("SELECT id FROM sys_product_feature WHERE feature_code = :c"),
            {"c": code},
        ).fetchone()
        if row:
            feature_id_map[code] = int(row.id)

    for version_code, target_codes in VERSION_TARGET.items():
        ver_row = conn.execute(
            text(
                "SELECT id FROM sys_product_version "
                "WHERE version_code = :code AND is_deleted = 0"
            ),
            {"code": version_code},
        ).fetchone()
        if not ver_row:
            print(f"  [SKIP] 版本 {version_code} 不存在")
            continue
        version_id = int(ver_row.id)
        print(f"  -- 版本 {version_code} (id={version_id}) --")

        # 删除旧运力 feature 关联
        for code, old_fid in legacy_id_map.items():
            cnt = (
                conn.execute(
                    text(
                        "SELECT COUNT(*) FROM sys_version_feature "
                        "WHERE version_id = :v AND feature_id = :f"
                    ),
                    {"v": version_id, "f": old_fid},
                ).scalar()
                or 0
            )
            if cnt == 0:
                continue
            prefix = "DRY-RUN" if dry_run else "DELETE"
            print(
                f"     [{prefix}] 移除旧关联 {version_code} <-> {code} "
                f"(feature_id={old_fid})"
            )
            if not dry_run:
                conn.execute(
                    text(
                        "DELETE FROM sys_version_feature "
                        "WHERE version_id = :v AND feature_id = :f"
                    ),
                    {"v": version_id, "f": old_fid},
                )

        # 插入新运力 feature 关联（已存在则跳过）
        for code in target_codes:
            new_fid = feature_id_map.get(code)
            if not new_fid:
                print(f"     [WARN] {version_code} 缺少 feature_id 映射: {code}")
                continue
            existing = (
                conn.execute(
                    text(
                        "SELECT id, status FROM sys_version_feature "
                        "WHERE version_id = :v AND feature_id = :f"
                    ),
                    {"v": version_id, "f": new_fid},
                ).fetchone()
            )
            if existing:
                if int(existing.status) != 1:
                    prefix = "DRY-RUN" if dry_run else "UPDATE"
                    print(
                        f"     [{prefix}] 启用 {version_code} <-> {code} "
                        f"(feature_id={new_fid})"
                    )
                    if not dry_run:
                        conn.execute(
                            text(
                                "UPDATE sys_version_feature SET status = 1, "
                                "updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                            ),
                            {"id": int(existing.id)},
                        )
                continue
            prefix = "DRY-RUN" if dry_run else "INSERT"
            print(
                f"     [{prefix}] 新增 {version_code} <-> {code} "
                f"(feature_id={new_fid})"
            )
            if not dry_run:
                conn.execute(
                    text(
                        "INSERT INTO sys_version_feature ("
                        "  version_id, feature_id, status, "
                        "  created_at, updated_at, is_deleted"
                        ") VALUES ("
                        "  :v, :f, 1, "
                        "  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0"
                        ")"
                    ),
                    {"v": version_id, "f": new_fid},
                )


# ---------------------------------------------------------------------------
# Step 7: bump menu_version
# ---------------------------------------------------------------------------

def step7_bump_menu_version(conn: Connection, dry_run: bool):
    print()
    print("=" * 60)
    print("Step 7: 递增 sys_tenant.menu_version 强制客户端刷新菜单")
    print("=" * 60)
    cnt = (
        conn.execute(
            text("SELECT COUNT(*) FROM sys_tenant WHERE is_deleted = 0")
        ).scalar()
        or 0
    )
    prefix = "DRY-RUN" if dry_run else "BUMP"
    print(f"  [{prefix}] 共 {cnt} 个活跃租户，将 menu_version + 1")
    if not dry_run:
        conn.execute(
            text(
                "UPDATE sys_tenant SET menu_version = menu_version + 1 "
                "WHERE is_deleted = 0"
            )
        )


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="运力中心模块 v3 数据迁移（一次性，幂等）"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅打印将执行的操作，不写库",
    )
    args = parser.parse_args()

    print("运力中心模块 v3 数据迁移脚本")
    print(f"  dry_run = {args.dry_run}")

    engine = _build_engine()
    try:
        with engine.connect() as conn:
            step1_update_v3_menus(conn, args.dry_run)
            code_to_menu_id = step2_upsert_buttons(conn, args.dry_run)
            step3_migrate_role_menu(conn, code_to_menu_id, args.dry_run)
            step4_soft_delete_legacy_menus(conn, args.dry_run)
            feature_id_map = step5_upsert_features(conn, args.dry_run)
            step6_rebuild_version_features(conn, feature_id_map, args.dry_run)
            step7_bump_menu_version(conn, args.dry_run)
            if not args.dry_run:
                conn.commit()
    finally:
        engine.dispose()

    print()
    if args.dry_run:
        print("[DRY-RUN] 未写库。确认无误后去掉 --dry-run 重新执行。")
    else:
        print("[OK] v3 运力数据迁移完成")
        print("    后续：python -m scripts.platform_sync export 重新导出快照并 git commit。")


if __name__ == "__main__":
    main()
