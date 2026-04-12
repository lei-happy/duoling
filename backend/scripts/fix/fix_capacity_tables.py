"""
为已有租户补建运力模块表：biz_capacity + biz_capacity_log

用法：
    python scripts/fix/fix_capacity_tables.py              # 所有已初始化租户
    python scripts/fix/fix_capacity_tables.py tenant_code   # 指定租户
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect
from app.core.config import get_settings
from app.core.database import TenantBase

# 确保运力模型已导入，注册进 TenantBase.metadata
from app.modules.client.models.capacity import Capacity, CapacityLog  # noqa: F401

CAPACITY_TABLES = ["biz_capacity", "biz_capacity_log"]


def get_all_tenant_codes(settings) -> list:
    """从平台库获取所有 db_initialized=1 的租户编码"""
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tenant_code FROM sys_tenant "
            "WHERE is_deleted = 0 AND db_initialized = 1"
        ))
        codes = [row[0] for row in result]
    engine.dispose()
    return codes


def fix_capacity_tables(tenant_code: str, settings):
    """为单个租户补建运力表"""
    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)

    inspector = sa_inspect(engine)
    existing_tables = set(inspector.get_table_names())

    tables_to_create = [
        TenantBase.metadata.tables[name]
        for name in CAPACITY_TABLES
        if name in TenantBase.metadata.tables and name not in existing_tables
    ]

    if not tables_to_create:
        print(f"  [{tenant_code}] 运力表已存在，跳过")
    else:
        TenantBase.metadata.create_all(engine, tables=tables_to_create)
        created_names = [t.name for t in tables_to_create]
        print(f"  [{tenant_code}] 已补建: {created_names}")

    engine.dispose()


if __name__ == "__main__":
    settings = get_settings()

    if len(sys.argv) > 1:
        codes = [sys.argv[1]]
    else:
        codes = get_all_tenant_codes(settings)
        if not codes:
            print("未找到已初始化的租户库")
            sys.exit(0)
        print(f"找到 {len(codes)} 个已初始化的租户库: {codes}")

    for code in codes:
        try:
            fix_capacity_tables(code, settings)
        except Exception as e:
            print(f"  [{code}] 失败: {e}")

    print(f"\n完成！共处理 {len(codes)} 个租户库")
