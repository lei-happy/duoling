"""ORM ↔ snapshot drift 检查器

CLI:
  python -m scripts.migration.check                # 同时检查 tenant + platform
  python -m scripts.migration.check --tenant       # 仅租户库
  python -m scripts.migration.check --platform     # 仅平台库
  python -m scripts.migration.check --json         # 输出 JSON 便于 CI 解析

退出码：
  0  当前 ORM metadata 与 snapshot 一致（无 drift）
  1  存在 drift——必须先跑 `python -m scripts.migration.autogen ...`
     生成迁移文件 + 刷新 snapshot 后再 commit
  2  环境/配置错误（导入模型失败、snapshot 文件损坏等）

约束：本工具不连数据库，纯静态对比 ORM 类与 snapshot JSON；
      故可在任何 CI 环境（无 DB）安全运行。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from scripts.migration._paths import (
    PLATFORM_SNAPSHOT,
    TENANT_SNAPSHOT,
    ensure_backend_on_syspath,
)

ensure_backend_on_syspath()

from scripts.migration._imports import import_all_models  # noqa: E402
from scripts.migration._metadata import (  # noqa: E402
    annotate_table_tiers,
    diff_snapshots,
    load_snapshot,
    serialize_metadata,
)


def _check_one(label: str, base, snapshot_path: Path) -> Tuple[List[str], Dict]:
    """返回 (diff lines, current_serialized_dict)。"""
    annotate_table_tiers(base.metadata, base)
    current = serialize_metadata(base.metadata)
    snapshot = load_snapshot(snapshot_path)
    diffs = diff_snapshots(snapshot, current)
    return diffs, current


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ORM metadata vs snapshot drift checker（无需 DB）",
    )
    parser.add_argument("--tenant", action="store_true", help="仅检查 tenant_schema.json")
    parser.add_argument("--platform", action="store_true", help="仅检查 platform_schema.json")
    parser.add_argument("--json", dest="as_json", action="store_true",
                        help="输出 JSON 报告（CI 友好）")
    args = parser.parse_args()

    do_tenant = args.tenant or not (args.tenant or args.platform)
    do_platform = args.platform or not (args.tenant or args.platform)

    try:
        import_all_models()
        from app.core.database import PlatformBase, TenantBase
    except Exception as e:
        msg = f"[ERROR] 导入 ORM 模型失败：{type(e).__name__}: {e}"
        if args.as_json:
            print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
        else:
            print(msg, file=sys.stderr)
        return 2

    reports = {}
    if do_platform:
        diffs, _ = _check_one("platform", PlatformBase, PLATFORM_SNAPSHOT)
        reports["platform"] = diffs
    if do_tenant:
        diffs, _ = _check_one("tenant", TenantBase, TENANT_SNAPSHOT)
        reports["tenant"] = diffs

    has_drift = any(v for v in reports.values())

    if args.as_json:
        print(json.dumps(
            {"ok": not has_drift, "reports": reports},
            ensure_ascii=False, indent=2,
        ))
        return 1 if has_drift else 0

    print("\n========== Schema Drift Check ==========")
    for label, diffs in reports.items():
        print(f"\n>>> {label} ({len(diffs)} diffs)")
        if not diffs:
            print("  [OK] ORM metadata 与 snapshot 一致")
            continue
        for line in diffs:
            print(f"  {line}")

    print()
    if has_drift:
        print("=" * 50)
        print("[DRIFT] ORM 与 snapshot 不一致，须按以下流程处理：")
        print("  1) 生成迁移 stub 并自动刷新 snapshot：")
        print("       cd backend && python -m scripts.migration.autogen tenant   --name '<desc>'")
        print("       cd backend && python -m scripts.migration.autogen platform --name '<desc>'")
        print("  2) review/补全生成的迁移文件（默认值、回填等）")
        print("  3) 本地执行: python -m scripts.migration.runner   验证迁移幂等可应用")
        print("  4) 一并 git add 迁移文件 + snapshots/*.json 后再 commit")
        print("CI 会因本检查失败而阻塞合并。")
        print("=" * 50)
        return 1

    print("[OK] 无 drift，可以 commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
