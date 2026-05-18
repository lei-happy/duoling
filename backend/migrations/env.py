"""
Alembic 迁移环境配置（仅平台主库 zt_platform）。

为什么平台库走 Alembic 而租户库走自定义 runner？
  - 平台库全局唯一，Alembic 的单 DB 模型完美吻合
  - 租户库 N 个，且每个租户开通的 feature 不同 → metadata 子集动态变化
    Alembic 单 DB env 不便表达这种"按租户裁剪"的语义，故继续用
    backend/scripts/migration/runner.py 自管 biz_migration_log

事实源：
  - target_metadata = PlatformBase.metadata
  - 数据库 URL 取自 app.core.config.get_settings().platform_db_url_sync
  - 所有平台库模型必须在下方 import_all_models() 中被加载，
    否则 autogenerate 会漏表
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import get_settings
from app.core.database import PlatformBase

# ---------------------------------------------------------------------------
# 模型注册：必须在 target_metadata 之前完成全部导入
# ---------------------------------------------------------------------------
import app.modules.console.models  # noqa: F401
try:
    import app.modules.ai.models.platform  # noqa: F401
except Exception:
    pass
try:
    import app.modules.open.models  # noqa: F401
except Exception:
    pass


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = PlatformBase.metadata


def get_url() -> str:
    return get_settings().platform_db_url_sync


def run_migrations_offline() -> None:
    """以 'offline' 模式运行迁移（仅生成 SQL 脚本，不连 DB）。"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=False,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以 'online' 模式运行迁移（连接 DB 执行 DDL）。"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
