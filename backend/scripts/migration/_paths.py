"""迁移工具内部共享路径 / 常量"""

from __future__ import annotations

from pathlib import Path

_THIS = Path(__file__).resolve()
MIGRATION_DIR = _THIS.parent
BACKEND_DIR = MIGRATION_DIR.parents[1]

VERSIONS_DIR = MIGRATION_DIR / "versions"
SNAPSHOTS_DIR = MIGRATION_DIR / "snapshots"

TENANT_SNAPSHOT = SNAPSHOTS_DIR / "tenant_schema.json"
PLATFORM_SNAPSHOT = SNAPSHOTS_DIR / "platform_schema.json"

ALEMBIC_DIR = BACKEND_DIR / "migrations"
ALEMBIC_VERSIONS_DIR = ALEMBIC_DIR / "versions"
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


def ensure_backend_on_syspath() -> None:
    """所有 CLI 入口都需要把 backend/ 放到 sys.path[0]，方便 `import app.xxx`。"""
    import sys
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
