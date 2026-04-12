"""
同步 Client 端菜单数据到 sys_menu 表

菜单定义来自与本脚本同目录的 sys_menu.json（请保持与线上一致：从库导出或手工合并后再执行）。
默认按匹配键 upsert，与 JSON 中 client 且未删除的记录对齐。
使用 --insert-only 时仅插入缺失项，已存在的菜单不更新（避免覆盖库内最新配置）。

匹配规则：
  - 有 menu_code 的菜单：按 menu_code + app_type 匹配
  - 无 menu_code 的菜单：按 path + parent_id + app_type 匹配

用法：
    python scripts/seed/seed_client_menus.py
    python scripts/seed/seed_client_menus.py --insert-only

可选环境变量：
    SYS_MENU_JSON  覆盖默认的 sys_menu.json 路径（绝对路径或相对 cwd）
"""

import argparse
import copy
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


def _default_json_path() -> Path:
    return Path(__file__).resolve().parent / "sys_menu.json"


def load_client_menus_from_json(json_path: Path) -> list:
    """
    从 sys_menu 导出 JSON 中读取 app_type=client 且 is_deleted=0 的菜单，按 parent_id 组装为树。
    """
    with open(json_path, encoding="utf-8") as f:
        all_rows = json.load(f)

    rows = [
        r
        for r in all_rows
        if r.get("app_type") == "client" and int(r.get("is_deleted", 0)) == 0
    ]
    if not rows:
        raise ValueError(f"未在 {json_path} 中找到任何 app_type=client 且未删除的菜单行")

    by_id = {int(r["id"]): r for r in rows}
    ids = set(by_id.keys())

    children_of: dict[int, list] = defaultdict(list)
    for r in rows:
        pid = int(r["parent_id"])
        if pid in ids:
            children_of[pid].append(r)

    roots = [r for r in rows if int(r["parent_id"]) == 0]
    roots.sort(key=lambda x: (int(x.get("sort_order") or 0), int(x["id"])))
    for pid in children_of:
        children_of[pid].sort(
            key=lambda x: (int(x.get("sort_order") or 0), int(x["id"]))
        )

    keys = (
        "menu_name",
        "menu_code",
        "menu_type",
        "path",
        "component",
        "icon",
        "sort_order",
        "visible",
        "feature_code",
    )

    def row_to_item(r: dict) -> dict:
        item = {}
        for k in keys:
            v = r.get(k)
            if k == "menu_code" and v == "":
                item[k] = None
            elif k == "feature_code" and v == "":
                item[k] = ""
            else:
                item[k] = v
        if "visible" not in item or item["visible"] is None:
            item["visible"] = 1
        return item

    def build(r: dict) -> dict:
        item = row_to_item(r)
        cid = int(r["id"])
        ch = children_of.get(cid)
        if ch:
            item["children"] = [build(x) for x in ch]
        return item

    return [build(r) for r in roots]


def upsert_menus(conn, menus, parent_id=0, insert_only: bool = False):
    """
    递归同步菜单树（与 JSON 中 client 菜单定义一致）。

    insert_only=False：已存在则 UPDATE。
    insert_only=True：已存在则跳过更新，仍递归子节点（用于补全新菜单而不改已有行）。

    匹配规则：
      - 有 menu_code 的菜单：按 menu_code + app_type 匹配（跨父级唯一）
      - 无 menu_code 的菜单：按 path + parent_id + app_type 匹配（避免改名导致重复）
    """
    for menu in menus:
        children = menu.pop("children", None)
        menu_code = menu.get("menu_code")
        menu_path = menu.get("path")
        visible = menu.get("visible", 1)

        if menu_code:
            result = conn.execute(
                text(
                    "SELECT id FROM sys_menu "
                    "WHERE menu_code = :code AND app_type = 'client' AND is_deleted = 0"
                ),
                {"code": menu_code},
            )
        else:
            result = conn.execute(
                text(
                    "SELECT id FROM sys_menu "
                    "WHERE path = :path AND app_type = 'client' "
                    "AND parent_id = :pid AND is_deleted = 0"
                ),
                {"path": menu_path, "pid": parent_id},
            )

        existing_id = result.scalar()

        if existing_id:
            if not insert_only:
                conn.execute(
                    text(
                        "UPDATE sys_menu SET "
                        "menu_name = :menu_name, menu_code = :menu_code, "
                        "menu_type = :menu_type, path = :path, component = :component, "
                        "icon = :icon, sort_order = :sort_order, visible = :visible, "
                        "feature_code = :feature_code, parent_id = :parent_id "
                        "WHERE id = :id"
                    ),
                    {
                        "id": existing_id,
                        "parent_id": parent_id,
                        "menu_name": menu["menu_name"],
                        "menu_code": menu_code,
                        "menu_type": menu["menu_type"],
                        "path": menu_path,
                        "component": menu.get("component"),
                        "icon": menu.get("icon"),
                        "sort_order": menu.get("sort_order", 0),
                        "visible": visible,
                        "feature_code": menu.get("feature_code"),
                    },
                )
                print(f"  更新菜单: {menu['menu_name']} (id={existing_id})")
            else:
                print(f"  跳过已存在: {menu['menu_name']} (id={existing_id})")
            menu_id = existing_id
        else:
            conn.execute(
                text(
                    "INSERT INTO sys_menu "
                    "(parent_id, menu_name, menu_code, menu_type, path, component, "
                    "icon, sort_order, visible, status, app_type, feature_code, is_deleted) "
                    "VALUES (:parent_id, :menu_name, :menu_code, :menu_type, :path, "
                    ":component, :icon, :sort_order, :visible, 1, 'client', :feature_code, 0)"
                ),
                {
                    "parent_id": parent_id,
                    "menu_name": menu["menu_name"],
                    "menu_code": menu_code,
                    "menu_type": menu["menu_type"],
                    "path": menu_path,
                    "component": menu.get("component"),
                    "icon": menu.get("icon"),
                    "sort_order": menu.get("sort_order", 0),
                    "visible": visible,
                    "feature_code": menu.get("feature_code"),
                },
            )
            result = conn.execute(text("SELECT LAST_INSERT_ID()"))
            menu_id = result.scalar()
            print(
                f"  新增菜单: {menu['menu_name']} (id={menu_id}, feature_code={menu.get('feature_code')})"
            )

        if children:
            upsert_menus(conn, children, parent_id=menu_id, insert_only=insert_only)


def main():
    parser = argparse.ArgumentParser(description="同步 Client 端菜单到 sys_menu")
    parser.add_argument(
        "--insert-only",
        action="store_true",
        help="仅插入 JSON 中有而库中无的菜单，已匹配到的记录不执行 UPDATE",
    )
    args = parser.parse_args()
    env_path = (os.environ.get("SYS_MENU_JSON") or "").strip()
    json_path = (
        Path(env_path).expanduser()
        if env_path
        else _default_json_path()
    )
    if not json_path.is_file():
        print(f"错误: 找不到菜单 JSON 文件: {json_path}", file=sys.stderr)
        print("请将 sys_menu 导出为 backend/scripts/seed/sys_menu.json，或设置 SYS_MENU_JSON。", file=sys.stderr)
        sys.exit(1)

    settings = get_settings()
    db_name = settings.platform_database_name
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{db_name}?charset=utf8mb4"
    )
    engine = create_engine(url)

    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = :db AND table_name = 'sys_menu' "
                "AND column_name = 'feature_code'"
            ),
            {"db": db_name},
        )
        if result.scalar() == 0:
            print("添加 feature_code 列...")
            conn.execute(
                text(
                    "ALTER TABLE sys_menu ADD COLUMN feature_code VARCHAR(50) DEFAULT NULL "
                    "COMMENT '关联功能编码' AFTER app_type"
                )
            )
            conn.execute(text("CREATE INDEX idx_feature_code ON sys_menu (feature_code)"))
            conn.commit()
            print("feature_code 列已添加")

    menus = load_client_menus_from_json(json_path)
    menus = copy.deepcopy(menus)

    with engine.connect() as conn:
        mode = "insert-only（仅补全缺失）" if args.insert_only else "upsert（存在则更新）"
        print(f"\n从 {json_path} 加载 Client 菜单，开始同步… 模式: {mode}")
        upsert_menus(conn, menus, insert_only=args.insert_only)
        conn.commit()

    engine.dispose()
    print("\nClient 端菜单同步完成！")


if __name__ == "__main__":
    main()
