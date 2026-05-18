"""自动生成迁移文件 stub（runner 风格 / Alembic 风格）

CLI:
  # 租户库（输出到 scripts/migration/versions/）
  python -m scripts.migration.autogen tenant --name "add waybill region"

  # 平台库（输出到 alembic/versions/，调 alembic 自带 autogenerate）
  python -m scripts.migration.autogen platform --name "add ai prompt template"

工作机制（tenant 模式）：
  1. 读取 snapshots/tenant_schema.json 作为「上次对齐」基线
  2. 加载当前 TenantBase.metadata 序列化为新快照
  3. 通过 _metadata.compute_ops 计算结构化 ops 列表
  4. 渲染成 versions/<id>_<slug>.py 模板，含：
       - MIGRATION_ID（YYYYMMDD_NNN）
       - REQUIRES_TABLES 自动推断
       - upgrade(conn, tenant_code) 函数体（幂等 information_schema 自检 + ALTER）
  5. 同步刷新 snapshots/tenant_schema.json
  6. 提示开发者必看的 TODO（NOT NULL 列回填等）

工作机制（platform 模式）：
  1. 直接 shell out 到 `alembic revision --autogenerate -m '<name>'`
     （依赖 alembic 真连一次平台库做 schema 反射）
  2. 完成后刷新 snapshots/platform_schema.json
  3. 让开发者人工 review alembic/versions/<rev>_<slug>.py

设计取舍：
  * 租户库不走 alembic：alembic 是单 DB 模型，多租户场景里要么环境变量切库
    多次跑、要么自己写并发执行——和现有 runner 形态冲突，且 runner 已经在
    管 biz_migration_log。所以租户保持 runner 风格，autogen 自己渲染模板。
  * 渲染采用 information_schema + DATABASE() 检测列 / 索引存在性，幂等，
    与现有 versions/ 下示例文件保持一致。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.migration._paths import (
    ALEMBIC_INI,
    BACKEND_DIR,
    PLATFORM_SNAPSHOT,
    TENANT_SNAPSHOT,
    VERSIONS_DIR,
    ensure_backend_on_syspath,
)

ensure_backend_on_syspath()

from scripts.migration._imports import import_all_models  # noqa: E402
from scripts.migration._metadata import (  # noqa: E402
    annotate_table_tiers,
    compute_ops,
    dump_snapshot,
    load_snapshot,
    serialize_metadata,
)


# ---------------------------------------------------------------------------
# tenant 模式
# ---------------------------------------------------------------------------
def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_") or "auto"


def _next_migration_id(today: _dt.date, existing_ids: List[str]) -> str:
    """同一天内 NNN 自增；YYYYMMDD_NNN。"""
    prefix = today.strftime("%Y%m%d")
    today_seqs = [
        int(mid.split("_", 1)[1])
        for mid in existing_ids
        if mid.startswith(prefix + "_") and mid.split("_", 1)[1].isdigit()
    ]
    seq = (max(today_seqs) + 1) if today_seqs else 1
    return f"{prefix}_{seq:03d}"


def _scan_existing_ids() -> List[str]:
    out: List[str] = []
    if not VERSIONS_DIR.exists():
        return out
    for p in VERSIONS_DIR.glob("*.py"):
        if p.name.startswith("_"):
            continue
        m = re.match(r"^(\d{8}_\d{3})_", p.name)
        if m:
            out.append(m.group(1))
    return out


def _columns_to_set_clause(col: Dict[str, Any]) -> str:
    """渲染 ADD COLUMN / MODIFY COLUMN 时的列定义片段。"""
    parts: List[str] = [f"`{col['name']}` {col['type']}"]
    parts.append("NULL" if col.get("nullable") else "NOT NULL")
    sd = col.get("server_default")
    if sd is not None:
        # 简单识别：纯数字/now()/CURRENT_TIMESTAMP/字符串
        sd_str = str(sd)
        if sd_str.lower() in ("now()", "current_timestamp"):
            parts.append("DEFAULT CURRENT_TIMESTAMP")
        elif re.fullmatch(r"-?\d+(\.\d+)?", sd_str):
            parts.append(f"DEFAULT {sd_str}")
        else:
            esc = sd_str.replace("'", "''")
            parts.append(f"DEFAULT '{esc}'")
    if col.get("comment"):
        c = col["comment"].replace("'", "''")
        parts.append(f"COMMENT '{c}'")
    return " ".join(parts)


def _render_create_table(table: Dict[str, Any]) -> str:
    """对 runner Phase 1 已经能覆盖建表的场景，create_table 我们倾向于不在
    versioned migration 里重复 DDL（避免与 metadata.create_all 冲突），
    只留一行 TODO 注释，建议把表加到 sys_product_feature.required_tables。"""
    return (
        f"    # NOTE: 新表 `{table['name']}` —— 推荐直接由 runner Phase 1 "
        f"(feature.required_tables) 自动建表。\n"
        f"    # 如本迁移确实需要在租户库强建该表，请改用 metadata.create_all 风格。\n"
        f"    # 此处空操作。\n"
    )


def _render_drop_table(table_name: str) -> str:
    return (
        f"    # 危险操作：删除表 `{table_name}`，autogen 仅生成 TODO，请人工审核\n"
        f"    # conn.execute(text(\"DROP TABLE IF EXISTS `{table_name}`\"))\n"
        f"    raise NotImplementedError(\n"
        f"        \"删除表 `{table_name}` 需人工 review 后启用此迁移\"\n"
        f"    )\n"
    )


def _render_add_column(table_name: str, col: Dict[str, Any]) -> str:
    col_def = _columns_to_set_clause(col)
    nullable_warning = ""
    if not col.get("nullable") and col.get("server_default") is None:
        nullable_warning = (
            f"    # TODO: `{col['name']}` 是 NOT NULL 且无 server_default —— "
            f"线上存量数据将报错，需要在 ALTER 之前先 UPDATE 回填，"
            f"或改成允许 NULL / 提供默认值。\n"
        )
    return (
        f"{nullable_warning}"
        f"    if not _col_exists(conn, \"{table_name}\", \"{col['name']}\"):\n"
        f"        conn.execute(text(\n"
        f"            \"ALTER TABLE `{table_name}` ADD COLUMN {col_def}\"\n"
        f"        ))\n"
    )


def _render_drop_column(table_name: str, column_name: str) -> str:
    return (
        f"    # 危险操作：删除列 `{table_name}.{column_name}`，会丢数据，请人工 review\n"
        f"    # if _col_exists(conn, \"{table_name}\", \"{column_name}\"):\n"
        f"    #     conn.execute(text(\n"
        f"    #         \"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`\"\n"
        f"    #     ))\n"
        f"    raise NotImplementedError(\n"
        f"        \"删除列 `{table_name}.{column_name}` 需人工 review 后启用此迁移\"\n"
        f"    )\n"
    )


def _render_alter_column(
    table_name: str, column_name: str,
    old: Dict[str, Any], new: Dict[str, Any],
) -> str:
    col_def = _columns_to_set_clause(new)
    notes = []
    for k in ("type", "nullable", "server_default", "comment"):
        if old.get(k) != new.get(k):
            notes.append(f"# - {k}: {old.get(k)!r} -> {new.get(k)!r}")
    notes_block = ("\n    " + "\n    ".join(notes)) if notes else ""
    return (
        f"    # ALTER `{table_name}.{column_name}`{notes_block}\n"
        f"    if _col_exists(conn, \"{table_name}\", \"{column_name}\"):\n"
        f"        conn.execute(text(\n"
        f"            \"ALTER TABLE `{table_name}` MODIFY COLUMN {col_def}\"\n"
        f"        ))\n"
    )


def _render_add_index(table_name: str, index: Dict[str, Any]) -> str:
    cols = ", ".join(f"`{c}`" for c in index.get("columns", []))
    name = index.get("name") or f"ix_{table_name}_{'_'.join(index.get('columns') or [])}"
    unique_kw = "UNIQUE " if index.get("unique") else ""
    return (
        f"    if not _index_exists(conn, \"{table_name}\", \"{name}\"):\n"
        f"        conn.execute(text(\n"
        f"            \"CREATE {unique_kw}INDEX `{name}` "
        f"ON `{table_name}` ({cols})\"\n"
        f"        ))\n"
    )


def _render_drop_index(table_name: str, index_name: str) -> str:
    return (
        f"    if _index_exists(conn, \"{table_name}\", \"{index_name}\"):\n"
        f"        conn.execute(text(\n"
        f"            \"DROP INDEX `{index_name}` ON `{table_name}`\"\n"
        f"        ))\n"
    )


def _render_add_unique(table_name: str, uq: Dict[str, Any]) -> str:
    cols = ", ".join(f"`{c}`" for c in uq.get("columns", []))
    name = uq.get("name") or f"uq_{table_name}_{'_'.join(uq.get('columns') or [])}"
    return (
        f"    if not _index_exists(conn, \"{table_name}\", \"{name}\"):\n"
        f"        conn.execute(text(\n"
        f"            \"ALTER TABLE `{table_name}` "
        f"ADD CONSTRAINT `{name}` UNIQUE ({cols})\"\n"
        f"        ))\n"
    )


def _render_drop_unique(table_name: str, name: str) -> str:
    return (
        f"    if _index_exists(conn, \"{table_name}\", \"{name}\"):\n"
        f"        conn.execute(text(\n"
        f"            \"ALTER TABLE `{table_name}` DROP INDEX `{name}`\"\n"
        f"        ))\n"
    )


def _render_op(op: Dict[str, Any]) -> str:
    kind = op["op"]
    if kind == "create_table":
        return _render_create_table(op["table"])
    if kind == "drop_table":
        return _render_drop_table(op["table_name"])
    if kind == "add_column":
        return _render_add_column(op["table_name"], op["column"])
    if kind == "drop_column":
        return _render_drop_column(op["table_name"], op["column_name"])
    if kind == "alter_column":
        return _render_alter_column(
            op["table_name"], op["column_name"], op["old"], op["new"],
        )
    if kind == "add_index":
        return _render_add_index(op["table_name"], op["index"])
    if kind == "drop_index":
        return _render_drop_index(op["table_name"], op["index_name"])
    if kind == "add_unique":
        return _render_add_unique(op["table_name"], op["unique"])
    if kind == "drop_unique":
        return _render_drop_unique(op["table_name"], op["unique_name"])
    return f"    # 未识别 op: {op!r}\n"


def _required_tables_from_ops(ops: List[Dict[str, Any]]) -> List[str]:
    """REQUIRES_TABLES = 本次迁移涉及的所有「现存表」名（去重）。"""
    out = set()
    for op in ops:
        kind = op["op"]
        if kind == "create_table":
            continue  # 新表无前置要求
        if "table_name" in op:
            out.add(op["table_name"])
    return sorted(out)


_FILE_TEMPLATE = '''"""{name}

Auto-generated by `python -m scripts.migration.autogen tenant`.

请人工 review，重点检查：
  * 新增 NOT NULL 列：是否需要先 UPDATE 回填，或改成允许 NULL / 提供默认值
  * 改类型 / 改长度：是否会截断现有数据
  * 索引/唯一约束变更：是否会破坏线上正在运行的查询
  * 删除/重命名：autogen 默认生成 NotImplementedError，需人工启用并测试
"""

from sqlalchemy import text

MIGRATION_ID = "{mid}"
MIGRATION_NAME = "{name}"

REQUIRES_TABLES = {requires_tables!r}


_COL_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :tn
      AND column_name = :cn
    LIMIT 1
    """
)

_INDEX_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = :tn
      AND index_name = :ix
    LIMIT 1
    """
)


def _col_exists(conn, table_name: str, column_name: str) -> bool:
    return conn.execute(
        _COL_EXISTS_SQL, {{"tn": table_name, "cn": column_name}}
    ).fetchone() is not None


def _index_exists(conn, table_name: str, index_name: str) -> bool:
    return conn.execute(
        _INDEX_EXISTS_SQL, {{"tn": table_name, "ix": index_name}}
    ).fetchone() is not None


def upgrade(conn, tenant_code: str) -> None:
{body}
'''


def _render_file(mid: str, name: str, ops: List[Dict[str, Any]]) -> str:
    body_blocks: List[str] = []
    for op in ops:
        body_blocks.append(_render_op(op))
    body = "\n".join(body_blocks) if body_blocks else "    pass\n"
    requires = _required_tables_from_ops(ops)
    safe_name = name.replace('"', '\\"')
    return _FILE_TEMPLATE.format(
        mid=mid,
        name=safe_name,
        requires_tables=requires,
        body=body,
    )


def autogen_tenant(name: str, *, dry_run: bool = False) -> int:
    import_all_models()
    from app.core.database import TenantBase

    annotate_table_tiers(TenantBase.metadata, TenantBase)
    new_snap = serialize_metadata(TenantBase.metadata)
    old_snap = load_snapshot(TENANT_SNAPSHOT)
    ops = compute_ops(old_snap, new_snap)

    if not ops:
        print("[OK] 当前 ORM 与 snapshot 一致，无需生成迁移文件")
        return 0

    today = _dt.date.today()
    mid = _next_migration_id(today, _scan_existing_ids())
    slug = _slugify(name)
    filename = f"{mid}_{slug}.py"
    out_path = VERSIONS_DIR / filename

    content = _render_file(mid, name, ops)

    print("\n========== 检测到 schema 变更（tenant） ==========")
    print(f"待生成迁移文件: scripts/migration/versions/{filename}")
    print(f"涉及操作 {len(ops)} 个：")
    for op in ops:
        kind = op["op"]
        if "table_name" in op:
            tn = op["table_name"]
            extra = (
                op.get("column_name")
                or op.get("index_name")
                or op.get("unique_name")
                or (op.get("column") or {}).get("name")
                or (op.get("index") or {}).get("name")
                or (op.get("unique") or {}).get("name")
                or ""
            )
            print(f"  - {kind}: {tn}.{extra}")
        elif kind == "create_table":
            print(f"  - {kind}: {op['table']['name']}")

    if dry_run:
        print("\n[dry-run] 不写文件、不更新 snapshot")
        return 0

    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"\n[OK] 已写入 {out_path.relative_to(BACKEND_DIR)}")

    dump_snapshot(TenantBase.metadata, TENANT_SNAPSHOT, base=TenantBase)
    print(f"[OK] 已刷新 {TENANT_SNAPSHOT.relative_to(BACKEND_DIR)}")

    print("\n下一步：")
    print("  1) 打开生成的 .py，按 TODO 注释补全（特别是 NOT NULL 列回填）")
    print("  2) 本地跑：python -m scripts.migration.runner --dry-run  确认计划")
    print("  3) 本地跑：python -m scripts.migration.runner            真实应用")
    print("  4) git add 同时提交 versions/*.py 与 snapshots/tenant_schema.json")
    return 0


# ---------------------------------------------------------------------------
# platform 模式
# ---------------------------------------------------------------------------
def autogen_platform(name: str, *, dry_run: bool = False) -> int:
    """调用 alembic 自带 autogenerate，再刷新 platform_schema.json。

    需要平台库可达（alembic 反射当前 DB schema）。如果你只是想在没有 DB
    的环境（CI）下生成 stub —— 那不可行；真发版人请在本地跑。
    """
    if not ALEMBIC_INI.exists():
        print(f"[ERROR] 找不到 alembic.ini：{ALEMBIC_INI}", file=sys.stderr)
        return 2

    if dry_run:
        print("[dry-run] 不实际调用 alembic")
        return 0

    print(f"[INFO] $ alembic revision --autogenerate -m '{name}'")
    try:
        from alembic.config import Config
        from alembic import command
        cfg = Config(str(ALEMBIC_INI))
        cfg.set_main_option("script_location", str(ALEMBIC_INI.parent / "migrations"))
        command.revision(cfg, autogenerate=True, message=name)
        rc = 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] 调用 alembic 失败：{e}", file=sys.stderr)
        return 2

    if rc != 0:
        print(f"[ERROR] alembic revision 退出码 {rc}", file=sys.stderr)
        return rc

    # alembic 生成完成 → 刷新 snapshot
    import_all_models()
    from app.core.database import PlatformBase
    dump_snapshot(PlatformBase.metadata, PLATFORM_SNAPSHOT, base=PlatformBase)
    print(f"[OK] 已刷新 {PLATFORM_SNAPSHOT.relative_to(BACKEND_DIR)}")
    print("\n下一步：人工 review backend/alembic/versions/<rev>_*.py，本地跑 alembic upgrade head")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="自动生成迁移文件 stub（tenant=runner 风格 / platform=alembic）",
    )
    sub = parser.add_subparsers(dest="target", required=True)

    p_t = sub.add_parser("tenant", help="生成租户库迁移文件（runner 风格）")
    p_t.add_argument("--name", required=True, help="迁移描述（用于文件名 + MIGRATION_NAME）")
    p_t.add_argument("--dry-run", action="store_true")

    p_p = sub.add_parser("platform", help="生成平台库迁移文件（alembic）")
    p_p.add_argument("--name", required=True)
    p_p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if args.target == "tenant":
        return autogen_tenant(args.name, dry_run=args.dry_run)
    if args.target == "platform":
        return autogen_platform(args.name, dry_run=args.dry_run)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
