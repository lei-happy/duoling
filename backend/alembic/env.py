"""
Alembic 迁移环境配置

支持平台库（zt_platform）的版本化迁移。
租户库的表结构通过 DatabaseManager.create_tenant_database / ensure_tenant_tables 管理，
渐进式建表仍走 metadata.create_all，与 Alembic 互不干扰。
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import get_settings
from app.core.database import PlatformBase

# 确保所有平台模型被导入以注册到 metadata
import app.modules.console.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = PlatformBase.metadata


def get_url():
    return get_settings().platform_db_url_sync


def run_migrations_offline() -> None:
    """以 'offline' 模式运行迁移（仅生成 SQL 脚本）"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以 'online' 模式运行迁移（直接连接数据库）"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
