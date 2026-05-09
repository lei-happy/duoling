"""
同步菜单数据到 sys_menu 表（支持 Client 端 与 Console 平台后台两种菜单）

事实源：
  - app_type=client   → backend/scripts/platform_sync/snapshots/client_menu.json
  - app_type=platform → backend/scripts/platform_sync/snapshots/platform_menu.json

由 `python -m scripts.platform_sync export` 在 dev 端生成；快照随代码 git push。

三种同步模式：
  默认（preserve-ui）: 已存在的菜单只更新结构字段（menu_name/menu_code/menu_type/path/
                       component/feature_code），保留数据库中用户配置的 icon/sort_order/visible。
  --force-all        : 已存在则全字段 UPDATE（覆盖所有字段，包括 icon/排序/可见性）。
  --insert-only      : 仅插入缺失项，已存在的菜单不更新。

`python -m scripts.platform_sync sync` 会以 --force-all 模式分别调用 client 和 platform。

匹配规则：
  - 有 _seed_id 时：按 (id + app_type) 主键匹配（最稳健）
  - 否则有 menu_code：按 menu_code + app_type 匹配
  - 否则按 path + parent_id + app_type 匹配

用法：
    python scripts/seed/seed_client_menus.py                            # 默认 client + preserve-ui
    python scripts/seed/seed_client_menus.py --force-all                # client 全字段覆盖
    python scripts/seed/seed_client_menus.py --app-type platform        # platform 后台菜单
    python scripts/seed/seed_client_menus.py --app-type platform --force-all

可选环境变量:
    SYS_MENU_JSON  覆盖默认事实源路径（一般不要使用，仅供应急覆盖）
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


def _default_json_path(app_type: str = "client") -> Path:
    """事实源：platform_sync 工具产出的菜单快照（按 app_type 选不同文件）。"""
    filename = "platform_menu.json" if app_type == "platform" else "client_menu.json"
    return (
        Path(__file__).resolve().parent.parent
        / "platform_sync"
        / "snapshots"
        / filename
    )


def load_client_menus_from_json(json_path: Path, app_type: str = "client") -> list:
    """
    从 sys_menu 导出 JSON 中读取指定 app_type 且 is_deleted=0 的菜单，按 parent_id 组装为树。
    """
    with open(json_path, encoding="utf-8") as f:
        all_rows = json.load(f)

    rows = [
        r
        for r in all_rows
        if r.get("app_type") == app_type and int(r.get("is_deleted", 0)) == 0
    ]
    if not rows:
        raise ValueError(f"未在 {json_path} 中找到任何 app_type={app_type} 且未删除的菜单行")

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
        # 透传 id，供 upsert 基于稳定主键定位老记录（用于 v2.0 重命名/路径变更）
        if "id" in r and r["id"] is not None:
            item["_seed_id"] = int(r["id"])
        return item

    def build(r: dict) -> dict:
        item = row_to_item(r)
        cid = int(r["id"])
        ch = children_of.get(cid)
        if ch:
            item["children"] = [build(x) for x in ch]
        return item

    return [build(r) for r in roots]


def upsert_menus(conn, menus, parent_id=0, *, mode: str = "preserve_ui", app_type: str = "client"):
    """
    递归同步菜单树（与 JSON 中菜单定义一致）。

    mode:
      "preserve_ui" : 已存在则只更新结构字段，保留 icon/sort_order/visible（默认）
      "force_all"   : 已存在则全字段 UPDATE
      "insert_only" : 已存在则跳过更新，仅递归子节点

    app_type:
      "client"   : 客户端菜单
      "platform" : Console 平台后台菜单

    匹配规则（按优先级）：
      1. JSON 中带 _seed_id 时优先按 (id + app_type) 主键匹配（最稳健）
      2. 否则按 menu_code + app_type 匹配（跨父级唯一）
      3. 否则按 path + parent_id + app_type 匹配（避免改名导致重复）
    """
    for menu in menus:
        children = menu.pop("children", None)
        menu_code = menu.get("menu_code")
        menu_path = menu.get("path")
        visible = menu.get("visible", 1)
        seed_id = menu.pop("_seed_id", None)

        existing_id = None
        if seed_id:
            result = conn.execute(
                text(
                    "SELECT id FROM sys_menu "
                    "WHERE id = :sid AND app_type = :app_type AND is_deleted = 0"
                ),
                {"sid": seed_id, "app_type": app_type},
            )
            existing_id = result.scalar()

        if not existing_id and menu_code:
            result = conn.execute(
                text(
                    "SELECT id FROM sys_menu "
                    "WHERE menu_code = :code AND app_type = :app_type AND is_deleted = 0"
                ),
                {"code": menu_code, "app_type": app_type},
            )
            existing_id = result.scalar()

        if not existing_id and not menu_code:
            result = conn.execute(
                text(
                    "SELECT id FROM sys_menu "
                    "WHERE path = :path AND app_type = :app_type "
                    "AND parent_id = :pid AND is_deleted = 0"
                ),
                {"path": menu_path, "pid": parent_id, "app_type": app_type},
            )
            existing_id = result.scalar()

        if existing_id:
            if mode == "force_all":
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
                print(f"  更新菜单(全字段): {menu['menu_name']} (id={existing_id})")
            elif mode == "preserve_ui":
                conn.execute(
                    text(
                        "UPDATE sys_menu SET "
                        "menu_name = :menu_name, menu_code = :menu_code, "
                        "menu_type = :menu_type, path = :path, component = :component, "
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
                        "feature_code": menu.get("feature_code"),
                    },
                )
                print(f"  更新菜单(保留UI): {menu['menu_name']} (id={existing_id})")
            else:
                print(f"  跳过已存在: {menu['menu_name']} (id={existing_id})")
            menu_id = existing_id
        else:
            # JSON 中带 _seed_id 时显式指定主键，保证新菜单 ID 与快照完全一致
            if seed_id:
                # 防御：检查该 ID 是否被其他 app_type 或 已软删除的同类记录占用
                conflict = conn.execute(
                    text(
                        "SELECT id, menu_name, app_type, is_deleted "
                        "FROM sys_menu WHERE id = :sid"
                    ),
                    {"sid": seed_id},
                ).fetchone()
                if conflict is not None:
                    fix_hint = (
                        "请先执行: python backend/scripts/fix/fix_client_menu_v2.py"
                        if app_type == "client"
                        else "请人工排查并清理 sys_menu 表中该 ID 的占用记录后重跑"
                    )
                    raise RuntimeError(
                        f"\n[ERROR] seed id={seed_id} ('{menu['menu_name']}', app_type={app_type}) 已被现有记录占用："
                        f"\n        existing: id={conflict.id} name='{conflict.menu_name}' "
                        f"app_type={conflict.app_type} is_deleted={conflict.is_deleted}"
                        f"\n        {fix_hint}"
                    )
                conn.execute(
                    text(
                        "INSERT INTO sys_menu "
                        "(id, parent_id, menu_name, menu_code, menu_type, path, component, "
                        "icon, sort_order, visible, status, app_type, feature_code, is_deleted) "
                        "VALUES (:id, :parent_id, :menu_name, :menu_code, :menu_type, :path, "
                        ":component, :icon, :sort_order, :visible, 1, :app_type, :feature_code, 0)"
                    ),
                    {
                        "id": seed_id,
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
                        "app_type": app_type,
                    },
                )
                menu_id = seed_id
            else:
                conn.execute(
                    text(
                        "INSERT INTO sys_menu "
                        "(parent_id, menu_name, menu_code, menu_type, path, component, "
                        "icon, sort_order, visible, status, app_type, feature_code, is_deleted) "
                        "VALUES (:parent_id, :menu_name, :menu_code, :menu_type, :path, "
                        ":component, :icon, :sort_order, :visible, 1, :app_type, :feature_code, 0)"
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
                        "app_type": app_type,
                    },
                )
                result = conn.execute(text("SELECT LAST_INSERT_ID()"))
                menu_id = result.scalar()
            print(
                f"  新增菜单({app_type}): {menu['menu_name']} (id={menu_id}, feature_code={menu.get('feature_code')})"
            )

        if children:
            upsert_menus(conn, children, parent_id=menu_id, mode=mode, app_type=app_type)


def main():
    parser = argparse.ArgumentParser(description="同步菜单数据到 sys_menu（支持 client / platform 两类）")
    parser.add_argument(
        "--app-type",
        choices=["client", "platform"],
        default="client",
        help="菜单类型：client（默认，客户端菜单）或 platform（Console 后台菜单）",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--insert-only",
        action="store_true",
        help="仅插入 JSON 中有而库中无的菜单，已匹配到的记录不执行 UPDATE",
    )
    group.add_argument(
        "--force-all",
        action="store_true",
        help="已存在的菜单全字段 UPDATE（包括 icon/sort_order/visible，会覆盖用户配置）",
    )
    args = parser.parse_args()

    if args.insert_only:
        mode = "insert_only"
    elif args.force_all:
        mode = "force_all"
    else:
        mode = "preserve_ui"

    app_type = args.app_type

    env_path = (os.environ.get("SYS_MENU_JSON") or "").strip()
    json_path = (
        Path(env_path).expanduser()
        if env_path
        else _default_json_path(app_type)
    )
    if not json_path.is_file():
        print(f"错误: 找不到菜单事实源: {json_path}", file=sys.stderr)
        print(
            "请先在 dev 环境跑：\n"
            f"    cd backend && python -m scripts.platform_sync export\n"
            f"以从 console API 生成 snapshots/{app_type}_menu.json，再 git push 部署。",
            file=sys.stderr,
        )
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

    menus = load_client_menus_from_json(json_path, app_type=app_type)
    menus_for_check = copy.deepcopy(menus)
    menus = copy.deepcopy(menus)

    mode_labels = {
        "preserve_ui": "preserve-ui（保留 icon/排序/可见性，仅更新结构字段）",
        "force_all": "force-all（全字段覆盖）",
        "insert_only": "insert-only（仅补全缺失）",
    }

    with engine.connect() as conn:
        print(f"\n从 {json_path} 加载 {app_type} 菜单，开始同步… 模式: {mode_labels[mode]}")
        upsert_menus(conn, menus, mode=mode, app_type=app_type)
        conn.commit()

    engine.dispose()
    print(f"\n{app_type} 端菜单同步完成！")

    # ---- 末尾自检：仅 client 类型扫描前端工程检查 component 引用 ----
    if app_type == "client":
        _check_missing_frontend_pages(menus_for_check)


def _flatten_components(items: list, out: list[dict]) -> None:
    for item in items:
        comp = item.get("component")
        if comp:
            out.append({
                "menu_name": item.get("menu_name"),
                "path": item.get("path"),
                "component": comp,
            })
        children = item.get("children")
        if children:
            _flatten_components(children, out)


def _check_missing_frontend_pages(menus: list) -> None:
    """
    根据 menu.component（如 "/resource/vehicle/index"）静态扫描
    frontend/client/src/views/<component>.vue 与 .../<component>/index.vue
    是否存在，打印缺失清单（不会失败）。

    若客户端工程不在仓库内（例如部署环境），自动跳过此检查。
    """
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    views_root = repo_root / "frontend" / "client" / "src" / "views"
    if not views_root.is_dir():
        print(f"[SKIP] 未找到客户端 views 目录，跳过前端页面校验：{views_root}")
        return

    flat: list[dict] = []
    _flatten_components(menus, flat)

    missing: list[dict] = []
    for item in flat:
        comp = (item["component"] or "").strip()
        if not comp:
            continue
        normalized = comp if comp.startswith("/") else "/" + comp
        candidates = [
            views_root.joinpath(*normalized.strip("/").split("/")).with_suffix(".vue"),
            views_root.joinpath(*normalized.strip("/").split("/")) / "index.vue",
        ]
        if not any(c.is_file() for c in candidates):
            missing.append(item)

    print("\n========== 前端页面校验 ==========")
    if not missing:
        print(f"[OK] {len(flat)} 个 component 引用全部存在")
    else:
        print(
            f"[警告] 共 {len(missing)} 个菜单 component 在客户端工程下找不到对应 .vue 文件，"
            "客户端将自动渲染「功能开发中」占位页："
        )
        for m in missing:
            print(f"  - {m['menu_name']}  path={m['path']}  component={m['component']}")
    print("==================================\n")


if __name__ == "__main__":
    main()
