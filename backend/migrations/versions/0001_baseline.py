"""baseline: ensure all platform tables from PlatformBase.metadata

Revision ID: 0001_baseline
Revises:
Create Date: 2026-05-18

设计意图
========

此 baseline 是 Alembic 接管 zt_platform 的第一条版本。它**故意**不内联
具体 DDL，而是直接调 `PlatformBase.metadata.create_all(bind)`：

  * 对全新部署：从空库出发，所有表一次性按当前 ORM 建好（与
    `scripts/init/init_platform_db.py` 行为一致，避免重复维护两份建表逻辑）。
  * 对存量平台库：deploy.sh 检测到 alembic_version 表不存在但平台库已有
    现成业务表 → 改走 `alembic stamp head`，跳过本 baseline 的 upgrade 体，
    只把版本号刻入 alembic_version；后续增量改动由真正的 versioned
    migration 接力。
  * `metadata.create_all` 自带 `IF NOT EXISTS` 语义，幂等，即使被误重跑
    也不会破坏现有数据。

后续真正的 schema 变更应该通过：
    python -m scripts.migration.autogen platform --name "<desc>"
生成下一条 alembic revision，并刷新 snapshots/platform_schema.json。
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _import_platform_models() -> None:
    """把所有平台库模型加载到 PlatformBase.metadata。"""
    import app.modules.console.models  # noqa: F401
    try:
        import app.modules.ai.models.platform  # noqa: F401
    except Exception:
        pass
    try:
        import app.modules.open.models  # noqa: F401
    except Exception:
        pass


def upgrade() -> None:
    _import_platform_models()
    from app.core.database import PlatformBase

    bind = op.get_bind()
    PlatformBase.metadata.create_all(bind)


def downgrade() -> None:
    """禁止回退 baseline：会删光平台库所有表。"""
    raise NotImplementedError(
        "baseline 不可 downgrade；如需回退请直接 DROP DATABASE 后重建"
    )
