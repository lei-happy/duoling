"""
快照差异比较

供 pull / verify 共用：将「新数据」与「旧快照」按业务主键做集合差，
输出新增 / 修改 / 删除三类，便于人类阅读。

主键约定：
  - client_menu / platform_menu : (menu_code or path)，因为环境间 id 不一致
  - product_feature              : feature_code
  - product_version              : version_code
  - version_feature              : (version_code, feature_code) 对集合
"""

from __future__ import annotations

import os
import getpass
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---- 业务主键提取 ----

def _menu_key(item: Dict[str, Any]) -> str:
    code = (item.get("menu_code") or "").strip()
    if code:
        return f"code:{code}"
    return f"path:{item.get('path') or ''}@{int(item.get('parent_id') or 0)}"


def _feature_key(item: Dict[str, Any]) -> str:
    return item.get("feature_code") or ""


def _version_key(item: Dict[str, Any]) -> str:
    return item.get("version_code") or ""


# 字段忽略清单：这些字段在不同环境天然不一致，对比时忽略
IGNORE_FIELDS = {
    "id",
    "created_at",
    "updated_at",
}


def _normalize_for_compare(item: Dict[str, Any]) -> Dict[str, Any]:
    """对比前规范化：忽略环境字段，且「缺 key」与显式 null 视为相同。"""
    return {k: v for k, v in item.items() if k not in IGNORE_FIELDS}


def _values_equal(a: Any, b: Any) -> bool:
    return a == b


def _dicts_equal_for_diff(old: Dict[str, Any], new: Dict[str, Any]) -> bool:
    keys = set(old.keys()) | set(new.keys())
    for k in keys:
        if k in IGNORE_FIELDS:
            continue
        if not _values_equal(old.get(k), new.get(k)):
            return False
    return True


# ---- 通用 diff 结构 ----

@dataclass
class ListDiff:
    added: List[Tuple[str, Dict[str, Any]]] = field(default_factory=list)
    removed: List[Tuple[str, Dict[str, Any]]] = field(default_factory=list)
    modified: List[Tuple[str, Dict[str, Any], Dict[str, Any]]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    @property
    def is_empty(self) -> bool:
        return self.total == 0


def active_snapshot_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """对比只认未删除记录。

    export / 线上拉取都会丢掉 is_deleted=1；seed 也不会插入它们。
    若手编快照把旧菜单改成墓碑却留在 JSON 里，diff 会永远显示「新增」，
    导致 deploy.sh update 的 apply 自检失败（exit=1）。
    """
    return [r for r in rows if int(r.get("is_deleted") or 0) == 0]


def diff_list(
    new_rows: List[Dict[str, Any]],
    old_rows: List[Dict[str, Any]],
    key_func,
) -> ListDiff:
    new_map = {key_func(r): r for r in new_rows}
    old_map = {key_func(r): r for r in old_rows}

    out = ListDiff()
    for k, r in new_map.items():
        if k not in old_map:
            out.added.append((k, r))
    for k, r in old_map.items():
        if k not in new_map:
            out.removed.append((k, r))
    for k, r in new_map.items():
        if k in old_map:
            new_norm = _normalize_for_compare(r)
            old_norm = _normalize_for_compare(old_map[k])
            if not _dicts_equal_for_diff(old_norm, new_norm):
                out.modified.append((k, old_norm, new_norm))
    return out


def diff_version_feature(
    new_map: Dict[str, List[str]], old_map: Dict[str, List[str]]
) -> ListDiff:
    """version_feature 是 dict[str, list[str]]，特殊处理：把对集合差展开"""
    new_pairs = {(v, fc) for v, codes in new_map.items() for fc in codes}
    old_pairs = {(v, fc) for v, codes in old_map.items() for fc in codes}

    out = ListDiff()
    for vc, fc in sorted(new_pairs - old_pairs):
        out.added.append((f"{vc}::{fc}", {"version_code": vc, "feature_code": fc}))
    for vc, fc in sorted(old_pairs - new_pairs):
        out.removed.append((f"{vc}::{fc}", {"version_code": vc, "feature_code": fc}))
    return out


# ---- 摘要打印 ----

def format_summary(name: str, d: ListDiff) -> str:
    if d.is_empty:
        return f"  [=] {name}: 无变化"
    parts = []
    if d.added:
        parts.append(f"新增 {len(d.added)}")
    if d.removed:
        parts.append(f"删除 {len(d.removed)}")
    if d.modified:
        parts.append(f"修改 {len(d.modified)}")
    return f"  [+/-] {name}: " + ", ".join(parts)


def format_detail(name: str, d: ListDiff, max_each: int = 20) -> List[str]:
    """逐条展开，每类截断到 max_each 项防止刷屏"""
    lines: List[str] = []
    if d.is_empty:
        return lines
    lines.append(f"\n--- {name} ---")
    for k, r in d.added[:max_each]:
        label = r.get("menu_name") or r.get("feature_name") or r.get("version_name") or k
        lines.append(f"  [+] {k}  {label}")
    if len(d.added) > max_each:
        lines.append(f"  ... 还有 {len(d.added) - max_each} 项新增（已折叠）")

    for k, r in d.removed[:max_each]:
        label = r.get("menu_name") or r.get("feature_name") or r.get("version_name") or k
        lines.append(f"  [-] {k}  {label}")
    if len(d.removed) > max_each:
        lines.append(f"  ... 还有 {len(d.removed) - max_each} 项删除（已折叠）")

    for k, old, new in d.modified[:max_each]:
        changes = []
        for field_name in sorted(set(old.keys()) | set(new.keys())):
            if old.get(field_name) != new.get(field_name):
                changes.append(
                    f"{field_name}: {old.get(field_name)!r} → {new.get(field_name)!r}"
                )
        lines.append(f"  [~] {k}: " + "; ".join(changes))
    if len(d.modified) > max_each:
        lines.append(f"  ... 还有 {len(d.modified) - max_each} 项修改（已折叠）")

    return lines


def current_user() -> str:
    """尽力获取当前操作者，CI 环境优先 env"""
    return (
        os.environ.get("GITHUB_ACTOR")
        or os.environ.get("USER")
        or os.environ.get("USERNAME")
        or getpass.getuser()
        or "unknown"
    )


# 各资源主键提取函数注册表，pull/verify 共用
KEY_FUNCS = {
    "client_menu": _menu_key,
    "platform_menu": _menu_key,
    "product_version": _version_key,
    "product_feature": _feature_key,
}
