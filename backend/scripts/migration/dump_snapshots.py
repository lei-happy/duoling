"""生成 / 刷新 schema snapshot 文件

用途：
  * 首次启用本机制时跑一次，得到「当前代码」的基线快照
  * autogen 工具内部调用，在写完迁移文件后同步更新

CLI:
  python -m scripts.migration.dump_snapshots               # 同时刷新两份
  python -m scripts.migration.dump_snapshots --tenant      # 仅租户库
  python -m scripts.migration.dump_snapshots --platform    # 仅平台库

输出：
  backend/scripts/migration/snapshots/tenant_schema.json
  backend/scripts/migration/snapshots/platform_schema.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.migration._paths import (
    PLATFORM_SNAPSHOT,
    SNAPSHOTS_DIR,
    TENANT_SNAPSHOT,
    ensure_backend_on_syspath,
)

ensure_backend_on_syspath()

from scripts.migration._imports import import_all_models  # noqa: E402
from scripts.migration._metadata import dump_snapshot  # noqa: E402


def dump_tenant() -> Path:
    import_all_models()
    from app.core.database import TenantBase
    dump_snapshot(TenantBase.metadata, TENANT_SNAPSHOT, base=TenantBase)
    return TENANT_SNAPSHOT


def dump_platform() -> Path:
    import_all_models()
    from app.core.database import PlatformBase
    dump_snapshot(PlatformBase.metadata, PLATFORM_SNAPSHOT, base=PlatformBase)
    return PLATFORM_SNAPSHOT


def main() -> int:
    parser = argparse.ArgumentParser(
        description="生成 / 刷新 ORM schema 快照文件（snapshots/*.json）",
    )
    parser.add_argument("--tenant", action="store_true", help="仅刷新 tenant_schema.json")
    parser.add_argument("--platform", action="store_true", help="仅刷新 platform_schema.json")
    args = parser.parse_args()

    do_tenant = args.tenant or not (args.tenant or args.platform)
    do_platform = args.platform or not (args.tenant or args.platform)

    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    if do_platform:
        out.append(dump_platform())
    if do_tenant:
        out.append(dump_tenant())
    for p in out:
        print(f"[OK] snapshot updated: {p.relative_to(p.parents[3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
