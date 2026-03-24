"""
初始化租户业务库
为新注册的企业创建独立数据库并初始化表结构

用法：
    python scripts/init_tenant_db.py <tenant_code>

示例：
    python scripts/init_tenant_db.py 1001
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings
from app.core.database import TenantBase

# 确保所有租户模型被导入
from app.modules.client.models import *  # noqa: F401, F403


def init_tenant_database(tenant_code: str):
    """
    为指定租户创建并初始化数据库

    Args:
        tenant_code: 租户编码
    """
    settings = get_settings()
    db_name = f"{settings.TENANT_DB_PREFIX}{tenant_code}"

    # 1. 创建数据库
    root_url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"?charset=utf8mb4"
    )
    engine = create_engine(root_url)
    with engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()
    engine.dispose()
    print(f"[OK] 数据库 {db_name} 已创建")

    # 2. 在新库中创建 core 层表结构
    from app.core.database import DatabaseManager
    core_tables = DatabaseManager.get_tables_by_tier("core")
    tenant_engine = create_engine(settings.tenant_db_url_sync(tenant_code))
    TenantBase.metadata.create_all(tenant_engine, tables=core_tables)
    tenant_engine.dispose()
    table_names = [t.name for t in core_tables]
    print(f"[OK] 租户库 {db_name} core 层表已初始化: {table_names}")

    return db_name


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/init_tenant_db.py <tenant_code>")
        print("示例: python scripts/init_tenant_db.py 1001")
        sys.exit(1)

    code = sys.argv[1]
    init_tenant_database(code)
    print(f"\n租户库初始化完成！租户编码: {code}")
