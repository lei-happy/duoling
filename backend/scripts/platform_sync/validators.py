"""
快照离线校验

输入是 5 份「内存中」的导出结果 dict / list，输出是问题列表。
校验项：
  1. 唯一性
     - product_feature[*].feature_code 唯一
     - product_version[*].version_code 唯一
     - client_menu[*].menu_code 唯一（忽略空串）
     - platform_menu[*].menu_code 唯一（忽略空串）
  2. 引用完整性
     - client_menu[*].feature_code 必须在 product_feature 闭包内（或为空/None）
     - version_feature[ver][*] 引用的 feature_code 必须存在
     - version_feature 顶层键（version_code）必须在 product_version 中存在
  3. 数据完整性
     - menu_code 与 feature_code 不允许首尾空白
     - menu 树不允许出现父节点缺失（parent_id 不在已知 id 集合且 != 0）

任何一项 ERROR 都会让 pull/verify 中止；WARN 仅打印不阻塞。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# 导出器键名常量，避免拼写错误
KEY_CLIENT_MENU = "client_menu"
KEY_PLATFORM_MENU = "platform_menu"
KEY_PRODUCT_VERSION = "product_version"
KEY_PRODUCT_FEATURE = "product_feature"
KEY_VERSION_FEATURE = "version_feature"


@dataclass
class ValidationReport:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "ValidationReport") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def format(self) -> str:
        lines: List[str] = []
        if self.errors:
            lines.append(f"[ERROR] 发现 {len(self.errors)} 项致命问题：")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append(f"[WARN] 发现 {len(self.warnings)} 项警告：")
            lines.extend(f"  - {w}" for w in self.warnings)
        if not lines:
            lines.append("[OK] 快照校验通过")
        return "\n".join(lines)


def _check_unique(
    items: List[Dict[str, Any]], field_name: str, label: str, ignore_empty: bool = True
) -> List[str]:
    seen: Dict[Any, int] = {}
    errors: List[str] = []
    for idx, item in enumerate(items):
        v = item.get(field_name)
        if not v and ignore_empty:
            continue
        if isinstance(v, str) and v != v.strip():
            errors.append(
                f"{label}[{idx}].{field_name}={v!r} 含首尾空白"
            )
        if v in seen:
            errors.append(
                f"{label}.{field_name}={v!r} 重复（idx {seen[v]} 与 {idx}）"
            )
        else:
            seen[v] = idx
    return errors


def validate_snapshots(
    snapshots: Dict[str, Any]
) -> ValidationReport:
    """
    snapshots 形如：
        {
            "client_menu": [...],
            "platform_menu": [...],
            "product_version": [...],
            "product_feature": [...],
            "version_feature": {"basic": [...], ...},
        }

    每一项都允许为 None（表示本次 pull --only 跳过了该项），跳过相关交叉校验。
    """
    report = ValidationReport()

    client_menu = snapshots.get(KEY_CLIENT_MENU)
    platform_menu = snapshots.get(KEY_PLATFORM_MENU)
    product_version = snapshots.get(KEY_PRODUCT_VERSION)
    product_feature = snapshots.get(KEY_PRODUCT_FEATURE)
    version_feature = snapshots.get(KEY_VERSION_FEATURE)

    # ---- 1. 唯一性 ----
    if isinstance(product_feature, list):
        report.errors.extend(
            _check_unique(product_feature, "feature_code", "product_feature", ignore_empty=False)
        )

    if isinstance(product_version, list):
        report.errors.extend(
            _check_unique(product_version, "version_code", "product_version", ignore_empty=False)
        )

    if isinstance(client_menu, list):
        report.errors.extend(
            _check_unique(client_menu, "menu_code", "client_menu", ignore_empty=True)
        )

    if isinstance(platform_menu, list):
        report.errors.extend(
            _check_unique(platform_menu, "menu_code", "platform_menu", ignore_empty=True)
        )

    # ---- 2. 引用完整性 ----
    feature_codes: Optional[set] = None
    if isinstance(product_feature, list):
        feature_codes = {
            f["feature_code"]
            for f in product_feature
            if f.get("feature_code")
        }

    if feature_codes is not None and isinstance(client_menu, list):
        for idx, m in enumerate(client_menu):
            fc = m.get("feature_code")
            if fc and fc not in feature_codes:
                report.errors.append(
                    f"client_menu[{idx}] (menu_name={m.get('menu_name')!r}) 引用了未定义的 "
                    f"feature_code={fc!r}（请先在 console「产品功能清单」中创建）"
                )

    version_codes: Optional[set] = None
    if isinstance(product_version, list):
        version_codes = {
            v["version_code"] for v in product_version if v.get("version_code")
        }

    if isinstance(version_feature, dict):
        if version_codes is not None:
            for vcode in version_feature.keys():
                if vcode not in version_codes:
                    report.errors.append(
                        f"version_feature 出现未知 version_code={vcode!r}（不在产品版本表中）"
                    )
        if feature_codes is not None:
            for vcode, codes in version_feature.items():
                for fc in codes:
                    if fc not in feature_codes:
                        report.errors.append(
                            f"version_feature[{vcode!r}] 引用了未定义的 feature_code={fc!r}"
                        )

    # ---- 3. 树结构 ----
    if isinstance(client_menu, list):
        report.warnings.extend(_check_menu_tree(client_menu, "client_menu"))
    if isinstance(platform_menu, list):
        report.warnings.extend(_check_menu_tree(platform_menu, "platform_menu"))

    # ---- 4. 未绑定版本的 feature 仅 WARN ----
    if isinstance(version_feature, dict) and feature_codes is not None:
        bound = set()
        for codes in version_feature.values():
            bound.update(codes)
        unbound = sorted(feature_codes - bound)
        if unbound:
            report.warnings.append(
                f"以下 {len(unbound)} 个 feature_code 未绑定到任何版本（客户端将永远不可见）：{unbound}"
            )

    return report


def _check_menu_tree(rows: List[Dict[str, Any]], label: str) -> List[str]:
    """检查菜单树是否有孤儿 parent_id"""
    ids = {int(r["id"]) for r in rows if r.get("id") is not None}
    warnings: List[str] = []
    for idx, r in enumerate(rows):
        pid = int(r.get("parent_id") or 0)
        if pid != 0 and pid not in ids:
            warnings.append(
                f"{label}[{idx}] (menu_name={r.get('menu_name')!r}) parent_id={pid} 不在快照内"
                f"（可能是父节点已被软删除而子节点未级联清理）"
            )
    return warnings
