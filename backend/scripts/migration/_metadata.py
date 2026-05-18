"""SQLAlchemy MetaData 序列化 / 反序列化 / 对比工具

用途：把 PlatformBase / TenantBase 的 metadata 落地为结构化 JSON 快照
（snapshots/*.json），作为「上一次代码与库结构集体对齐」的事实源。

设计目标：
  * 输出稳定（按表名/列名字典序），可直接 diff
  * 类型用 SQLAlchemy `String(...)` 形式的字符串表达，避免方言耦合
  * 仅捕获 schema 层信息：表 / 列 / 主键 / 唯一约束 / 索引 / 外键 / comment
    （不含 server_default 的 CASE 等动态表达式细节，避免无谓抖动）

使用方：
  * scripts.migration.check     - diff 当前 metadata vs snapshot
  * scripts.migration.autogen   - 生成迁移文件后刷新 snapshot
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import MetaData
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    Table,
    UniqueConstraint,
)


# ---------------------------------------------------------------------------
# 序列化
# ---------------------------------------------------------------------------
def _column_to_dict(col: Column) -> Dict[str, Any]:
    type_repr = str(col.type.compile(dialect=_mysql_dialect()))

    server_default_repr: Optional[str] = None
    if col.server_default is not None:
        arg = getattr(col.server_default, "arg", None)
        if arg is not None:
            try:
                server_default_repr = str(arg.text) if hasattr(arg, "text") else str(arg)
            except Exception:
                server_default_repr = repr(col.server_default)
        else:
            server_default_repr = repr(col.server_default)

    # SQLAlchemy 中 col.autoincrement 默认值是字符串 "auto"，所有列都不是 False；
    # 只在 PK 列上显式记录，避免 snapshot 噪声。
    if col.primary_key:
        if col.autoincrement is True:
            autoinc: Any = True
        elif col.autoincrement is False:
            autoinc = False
        else:
            autoinc = "auto"
    else:
        autoinc = None

    return {
        "name": col.name,
        "type": type_repr,
        "nullable": bool(col.nullable),
        "primary_key": bool(col.primary_key),
        "autoincrement": autoinc,
        "server_default": server_default_repr,
        "comment": col.comment,
    }


def _index_to_dict(idx: Index) -> Dict[str, Any]:
    return {
        "name": idx.name,
        "columns": [c.name for c in idx.expressions if hasattr(c, "name")],
        "unique": bool(idx.unique),
    }


def _uq_to_dict(uq: UniqueConstraint) -> Dict[str, Any]:
    return {
        "name": uq.name,
        "columns": [c.name for c in uq.columns],
    }


def _fk_to_dict(fk: ForeignKeyConstraint) -> Dict[str, Any]:
    return {
        "name": fk.name,
        "columns": [c.name for c in fk.columns],
        "referred_table": fk.referred_table.name if fk.referred_table is not None else None,
        "referred_columns": [el.column.name for el in fk.elements],
        "ondelete": fk.ondelete,
        "onupdate": fk.onupdate,
    }


def _pk_to_dict(pk: PrimaryKeyConstraint) -> Optional[List[str]]:
    cols = [c.name for c in pk.columns]
    return sorted(cols) if cols else None


def _table_to_dict(table: Table) -> Dict[str, Any]:
    columns = sorted(
        [_column_to_dict(c) for c in table.columns],
        key=lambda x: x["name"],
    )

    indexes = sorted(
        [_index_to_dict(i) for i in table.indexes],
        key=lambda x: (x["name"] or "", tuple(x["columns"])),
    )

    uniques = sorted(
        [
            _uq_to_dict(c)
            for c in table.constraints
            if isinstance(c, UniqueConstraint)
        ],
        key=lambda x: (x["name"] or "", tuple(x["columns"])),
    )

    fks = sorted(
        [
            _fk_to_dict(c)
            for c in table.constraints
            if isinstance(c, ForeignKeyConstraint)
        ],
        key=lambda x: (x["name"] or "", tuple(x["columns"])),
    )

    pk_cols: List[str] = []
    for c in table.constraints:
        if isinstance(c, PrimaryKeyConstraint):
            pk_cols = _pk_to_dict(c) or []
            break

    return {
        "name": table.name,
        "comment": table.comment,
        "table_tier": _resolve_table_tier(table),
        "columns": columns,
        "primary_key": pk_cols,
        "unique_constraints": uniques,
        "indexes": indexes,
        "foreign_keys": fks,
    }


def _resolve_table_tier(table: Table) -> Optional[str]:
    """从 ORM mapper 反查 __table_tier__；只租户库会用到。"""
    for mapper in list(table.metadata._sa_module_registry) if False else []:  # type: ignore[attr-defined]
        pass
    # 直接通过 metadata.registry 寻找
    registry = getattr(table.metadata, "_sa_module_registry", None)
    # 兼容方式：遍历 PlatformBase / TenantBase 的 mappers 由调用方在更上一层处理
    return getattr(table, "_tier_hint", None)


def _mysql_dialect():
    from sqlalchemy.dialects import mysql
    return mysql.dialect()


def serialize_metadata(metadata: MetaData) -> Dict[str, Any]:
    """把 MetaData 序列化为可比较的 dict（已稳定排序）。"""
    tables = sorted(metadata.tables.values(), key=lambda t: t.name)
    return {
        "schema_version": 1,
        "tables": [_table_to_dict(t) for t in tables],
    }


def annotate_table_tiers(metadata: MetaData, base) -> None:
    """把 ORM 类的 __table_tier__ 反向写到对应 Table 对象上，便于 snapshot 标注。

    `base` 必须是 DeclarativeBase（PlatformBase 或 TenantBase）。
    """
    try:
        mappers = list(base.registry.mappers)
    except Exception:
        return
    for mapper in mappers:
        cls = mapper.class_
        tier = getattr(cls, "__table_tier__", None)
        if tier and getattr(cls, "__table__", None) is not None:
            setattr(cls.__table__, "_tier_hint", tier)


# ---------------------------------------------------------------------------
# 落盘 / 读取
# ---------------------------------------------------------------------------
def dump_snapshot(metadata: MetaData, path: Path, *, base=None) -> None:
    if base is not None:
        annotate_table_tiers(metadata, base)
    data = serialize_metadata(metadata)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")


def load_snapshot(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "tables": []}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------
def _table_index(snap: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {t["name"]: t for t in snap.get("tables", [])}


def diff_snapshots(
    snap_old: Dict[str, Any], snap_new: Dict[str, Any],
) -> List[str]:
    """返回人类可读 diff 行；空列表表示无差异。

    粒度：表新增/删除、列新增/删除/改类型/改可空/改默认/改 comment、
          PK / UQ / Index / FK 增删。
    """
    diffs: List[str] = []
    old_tables = _table_index(snap_old)
    new_tables = _table_index(snap_new)

    added_tables = sorted(set(new_tables) - set(old_tables))
    removed_tables = sorted(set(old_tables) - set(new_tables))
    common_tables = sorted(set(old_tables) & set(new_tables))

    for tn in added_tables:
        diffs.append(f"[+TABLE] {tn}")
    for tn in removed_tables:
        diffs.append(f"[-TABLE] {tn}")
    for tn in common_tables:
        diffs.extend(_diff_one_table(old_tables[tn], new_tables[tn]))

    return diffs


def _diff_one_table(old: Dict[str, Any], new: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    tn = new["name"]

    if (old.get("comment") or "") != (new.get("comment") or ""):
        out.append(
            f"[~TABLE] {tn}: comment "
            f"{old.get('comment')!r} -> {new.get('comment')!r}"
        )

    old_cols = {c["name"]: c for c in old.get("columns", [])}
    new_cols = {c["name"]: c for c in new.get("columns", [])}
    for cn in sorted(set(new_cols) - set(old_cols)):
        out.append(f"[+COL] {tn}.{cn} :: {new_cols[cn]['type']}")
    for cn in sorted(set(old_cols) - set(new_cols)):
        out.append(f"[-COL] {tn}.{cn}")
    for cn in sorted(set(old_cols) & set(new_cols)):
        a, b = old_cols[cn], new_cols[cn]
        for key in ("type", "nullable", "primary_key", "server_default", "comment"):
            if a.get(key) != b.get(key):
                out.append(
                    f"[~COL] {tn}.{cn} {key}: {a.get(key)!r} -> {b.get(key)!r}"
                )

    out.extend(_diff_named_list(tn, "INDEX", old.get("indexes", []), new.get("indexes", [])))
    out.extend(_diff_named_list(tn, "UNIQUE", old.get("unique_constraints", []), new.get("unique_constraints", [])))
    out.extend(_diff_named_list(tn, "FK", old.get("foreign_keys", []), new.get("foreign_keys", [])))

    if old.get("primary_key") != new.get("primary_key"):
        out.append(
            f"[~PK] {tn}: {old.get('primary_key')} -> {new.get('primary_key')}"
        )
    return out


def _diff_named_list(
    tn: str, label: str,
    old_items: List[Dict[str, Any]], new_items: List[Dict[str, Any]],
) -> List[str]:
    """对比同类约束列表：按 (name 或 columns) 当 key。"""
    def _key(item: Dict[str, Any]) -> Tuple:
        return (item.get("name") or "", tuple(item.get("columns") or ()))
    om = {_key(i): i for i in old_items}
    nm = {_key(i): i for i in new_items}
    out: List[str] = []
    for k in sorted(set(nm) - set(om)):
        out.append(f"[+{label}] {tn}.{nm[k].get('name') or '/'.join(nm[k].get('columns') or [])}")
    for k in sorted(set(om) - set(nm)):
        out.append(f"[-{label}] {tn}.{om[k].get('name') or '/'.join(om[k].get('columns') or [])}")
    for k in sorted(set(om) & set(nm)):
        if om[k] != nm[k]:
            out.append(f"[~{label}] {tn}.{nm[k].get('name')}")
    return out


# ---------------------------------------------------------------------------
# 结构化 ops（autogen 用）
# ---------------------------------------------------------------------------
#
# Op 类型清单（每条都是一个 dict，"op" 字段为类型）：
#   {"op": "create_table",   "table": <table_dict>}
#   {"op": "drop_table",     "table_name": str}
#   {"op": "add_column",     "table_name": str, "column": <col_dict>}
#   {"op": "drop_column",    "table_name": str, "column_name": str}
#   {"op": "alter_column",   "table_name": str, "column_name": str,
#                            "old": <col_dict>, "new": <col_dict>}
#   {"op": "add_index",      "table_name": str, "index": <idx_dict>}
#   {"op": "drop_index",     "table_name": str, "index_name": str}
#   {"op": "add_unique",     "table_name": str, "unique": <uq_dict>}
#   {"op": "drop_unique",    "table_name": str, "unique_name": str}
#
# 暂不生成 add_fk / drop_fk / alter_pk —— 业务上极少出现，必要时手写迁移。


def compute_ops(
    snap_old: Dict[str, Any], snap_new: Dict[str, Any],
) -> List[Dict[str, Any]]:
    ops: List[Dict[str, Any]] = []
    old_tables = _table_index(snap_old)
    new_tables = _table_index(snap_new)

    for tn in sorted(set(new_tables) - set(old_tables)):
        ops.append({"op": "create_table", "table": new_tables[tn]})
    for tn in sorted(set(old_tables) - set(new_tables)):
        ops.append({"op": "drop_table", "table_name": tn})

    for tn in sorted(set(old_tables) & set(new_tables)):
        old = old_tables[tn]
        new = new_tables[tn]

        old_cols = {c["name"]: c for c in old.get("columns", [])}
        new_cols = {c["name"]: c for c in new.get("columns", [])}

        for cn in sorted(set(new_cols) - set(old_cols)):
            ops.append({"op": "add_column", "table_name": tn, "column": new_cols[cn]})
        for cn in sorted(set(old_cols) - set(new_cols)):
            ops.append({"op": "drop_column", "table_name": tn, "column_name": cn})
        for cn in sorted(set(old_cols) & set(new_cols)):
            a, b = old_cols[cn], new_cols[cn]
            # 仅检测对 schema 真有影响的属性
            if any(a.get(k) != b.get(k) for k in (
                "type", "nullable", "primary_key", "server_default", "comment",
            )):
                ops.append({
                    "op": "alter_column",
                    "table_name": tn,
                    "column_name": cn,
                    "old": a,
                    "new": b,
                })

        ops.extend(_named_list_ops(
            tn, "index", old.get("indexes", []), new.get("indexes", []),
        ))
        ops.extend(_named_list_ops(
            tn, "unique", old.get("unique_constraints", []),
            new.get("unique_constraints", []),
        ))

    return ops


def _named_list_ops(
    tn: str, kind: str,
    old_items: List[Dict[str, Any]], new_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    def _key(item: Dict[str, Any]) -> Tuple:
        return (item.get("name") or "", tuple(item.get("columns") or ()))

    om = {_key(i): i for i in old_items}
    nm = {_key(i): i for i in new_items}
    ops: List[Dict[str, Any]] = []
    for k in sorted(set(nm) - set(om)):
        ops.append({"op": f"add_{kind}", "table_name": tn, kind: nm[k]})
    for k in sorted(set(om) - set(nm)):
        name = om[k].get("name") or "_".join(om[k].get("columns") or [])
        ops.append({"op": f"drop_{kind}", "table_name": tn, f"{kind}_name": name})
    for k in sorted(set(om) & set(nm)):
        if om[k] != nm[k]:
            # 改约束 = 先 drop 再 add，保持语义清晰
            name = om[k].get("name") or "_".join(om[k].get("columns") or [])
            ops.append({"op": f"drop_{kind}", "table_name": tn, f"{kind}_name": name})
            ops.append({"op": f"add_{kind}", "table_name": tn, kind: nm[k]})
    return ops
